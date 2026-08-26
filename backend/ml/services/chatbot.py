"""
AI Financial Chatbot Service

Replaces the old rule-based chatbot with a Gemini-powered assistant that:
- Understands natural language and follow-up questions
- Has access to the user's real financial data (income, expenses, budgets)
- Has access to real market data and analytics
- Makes calculations (SIP, retirement, EMI, comparisons)
- Generates charts data where applicable
- Explains reasoning (no one-line answers)

When Gemini is unavailable, falls back to a local analytics-driven engine
that still provides data-backed answers.
"""

import json
import logging
import re
from datetime import date, timedelta
from typing import Any, Dict, List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.income import Income
from backend.models.expense import Expense
from backend.models.budget import Budget
from backend.ml.analytics.analysis import market_analysis_service
from backend.ml.analytics.metrics import analytics_engine
from backend.ml.analytics.technical import technical_analyzer
from backend.ml.llm.client import get_llm_client
from backend.ml.services.financial_health import FinancialHealthEngine
from backend.ml.services.wealth_projection import WealthProjector

logger = logging.getLogger(__name__)


class FinancialChatbot:
    """Gemini-powered financial assistant with analytics fallback."""

    SYSTEM_PROMPT = (
        "You are a senior, certified financial advisor AI for Indian investors. "
        "You provide detailed, reasoned, data-backed advice. You never give "
        "one-line answers. You always explain the 'why' behind recommendations. "
        "You mention real historical returns where relevant. You use ₹ for amounts. "
        "You are careful and include risk disclaimers. You support follow-up "
        "questions naturally."
    )

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.health_engine = FinancialHealthEngine(db, user_id)
        self.projector = WealthProjector()
        self.llm = get_llm_client()

    # ---- Public API ----
    def respond(self, message: str, history: List[Dict[str, str]] | None = None) -> Dict:
        """Generate a response to the user's message."""
        context = self._build_context()
        history = history or []

        if self.llm.available:
            response = self._llm_response(message, context, history)
            if response:
                return {"response": response, "confidence": 1.0, "source": "llm"}

        # Fallback to analytics-driven engine
        response, confidence = self._analytics_response(message, context)
        return {"response": response, "confidence": confidence, "source": "analytics"}

    # ---- Context Building ----
    def _build_context(self) -> Dict[str, Any]:
        """Gather user financial context + market context."""
        income, expense, savings = self._get_monthly_summary()
        health = self.health_engine.calculate_overall_health_score()

        # Market context (lightweight, cached)
        market_context = {}
        try:
            overview = market_analysis_service.market_overview()
            market_context = {
                "assets": overview["assets"][:5],
                "top_performing": overview["top_performing"],
            }
        except Exception as exc:
            logger.warning("Market context failed: %s", exc)

        return {
            "monthly_income": round(income, 2),
            "monthly_expense": round(expense, 2),
            "monthly_savings": round(savings, 2),
            "savings_ratio": round((savings / income * 100), 1) if income > 0 else 0,
            "financial_health": health,
            "market": market_context,
        }

    def _get_monthly_summary(self) -> Tuple[float, float, float]:
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        if today.month == 12:
            end_of_month = date(today.year + 1, 1, 1)
        else:
            end_of_month = date(today.year, today.month + 1, 1)

        income = (
            self.db.query(func.coalesce(func.sum(Income.amount), 0))
            .filter(Income.user_id == self.user_id, Income.received_date >= start_of_month, Income.received_date < end_of_month)
            .scalar()
        ) or 0
        expense = (
            self.db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(Expense.user_id == self.user_id, Expense.spent_at >= start_of_month, Expense.spent_at < end_of_month)
            .scalar()
        ) or 0
        return income, expense, income - expense

    # ---- LLM path ----
    def _llm_response(
        self, message: str, context: Dict[str, Any], history: List[Dict[str, str]]
    ) -> str:
        """Build a prompt and query the LLM."""
        context_str = json.dumps(context, indent=2, default=str)
        history_str = "\n".join(
            f"User: {m.get('user', '')}\nAssistant: {m.get('assistant', '')}"
            for m in history[-6:]
        )

        prompt = (
            f"User financial context (real data):\n{context_str}\n\n"
            f"Conversation history:\n{history_str}\n\n"
            f"User question: {message}\n\n"
            f"Provide a comprehensive answer with calculations and market-data-backed "
            f"reasoning. If the user asks about investing, suggest an allocation "
            f"with percentages and expected returns. If they mention amounts "
            f"(salary, SIP, goals), use them in projections."
        )
        return self.llm.generate(prompt, system=self.SYSTEM_PROMPT, max_tokens=1200, temperature=0.5) or ""

    # ---- Analytics fallback ----
    def _analytics_response(self, message: str, context: Dict[str, Any]) -> Tuple[str, float]:
        """Answer common questions using real analytics data."""
        msg = message.lower().strip()

        if any(k in msg for k in ["invest", "where to invest", "sip", "mutual fund"]):
            return self._answer_investment(context), 0.85
        if any(k in msg for k in ["compare", "vs", "versus", "fd", "fixed deposit"]):
            return self._answer_comparison(msg), 0.8
        if any(k in msg for k in ["buy", "reliance", "stock", "share", "tcs", "infy"]):
            return self._answer_stock(msg), 0.8
        if any(k in msg for k in ["retire", "retirement"]):
            return self._answer_retirement(msg, context), 0.75
        if any(k in msg for k in ["month", "year", "wealth", "future value", "10,000", "10000"]):
            return self._answer_wealth(msg, context), 0.85
        if any(k in msg for k in ["health", "score", "how am i doing"]):
            return self._answer_health(context), 0.95
        if any(k in msg for k in ["save", "saving", "budget", "expense", "spend"]):
            return self._answer_budget(context), 0.85
        if any(k in msg for k in ["market", "nifty", "sensex", "gold", "trend"]):
            return self._answer_market(), 0.8
        if any(k in msg for k in ["hello", "hi", "hey", "help", "what can you do"]):
            return self._answer_greeting(), 1.0

        return self._answer_general(context), 0.6

    def _answer_investment(self, context: Dict[str, Any]) -> str:
        income = context["monthly_income"]
        savings = context["monthly_savings"]
        health = context["financial_health"]["overall_score"]
        rule = ""

        if savings <= 0:
            rule = (
                f"Your monthly savings are ₹{savings:.0f} (negative/zero). Before investing, "
                f"focus on bridging this gap. Reduce discretionary expenses and build a "
                f"₹{max(context['monthly_expense'], 0) * 3:.0f} emergency fund first."
            )
            return rule

        capacity = savings * 0.7
        market = context.get("market", {}).get("assets", [])
        mf_line = ""
        if market:
            mf_cagr = market[0].get("cagr", 12)
            mf_line = (
                f"Based on 5-year real data, major indices/mutual funds returned around "
                f"{mf_cagr:.1f}% CAGR."
            )

        allocation = (
            f"Given your income of ₹{income:.0f}/mo and savings of ₹{savings:.0f}/mo, "
            f"you could invest about ₹{capacity:.0f}/month. {mf_line}\n\n"
            f"A balanced (Moderate) allocation would be:\n"
            f"• 35% Index Mutual Funds\n"
            f"• 20% Large Cap Stocks\n"
            f"• 12% Gold ETF\n"
            f"• 20% Fixed Deposit/Debt\n"
            f"• 13% Emergency cash buffer\n\n"
            f"This diversification reduces risk while capturing long-term growth. "
            f"Your financial health score is {health:.0f}/100, so "
            f"{'you are well-positioned to invest' if health >= 60 else 'focus on strengthening your savings before aggressive investing'}."
        )
        return allocation

    def _answer_comparison(self, msg: str) -> str:
        result = market_analysis_service.comparison(["NIFTY 50", "GOLD"])
        assets = result["assets"]
        nifty = assets.get("NIFTY 50", {})
        gold = assets.get("GOLD", {})
        nifty_name = "NIFTY 50"
        gold_name = "GOLD"

        if "fd" in msg or "fixed" in msg:
            fd_return = 6.5
            mf = nifty.get("cagr", 12)
            return (
                f"FD vs Mutual Fund comparison (based on real 5Y data):\n\n"
                f"• Fixed Deposit: ~{fd_return:.1f}% p.a., very low risk, capital protected\n"
                f"• Mutual Funds (Equity/Index): ~{mf:.1f}% 5Y CAGR, higher volatility (~{nifty.get('volatility', 15):.0f}%)\n\n"
                f"Over 5 years, investing ₹10,000/mo in an index fund could grow to "
                f"₹{self._sip_future_value(10000, 5, mf):.0f} vs ₹{self._sip_future_value(10000, 5, fd_return):.0f} in an FD. "
                f"However, FDs offer guaranteed returns while mutual funds carry market risk. "
                f"Many advisors suggest a mix (e.g., 70% equity fund + 30% FD)."
            )

        nifty_cagr = nifty.get("cagr", 0)
        gold_cagr = gold.get("cagr", 0)
        return (
            f"NIFTY 50 vs GOLD (5-year real data):\n\n"
            f"• NIFTY 50: {nifty_cagr:.1f}% CAGR, volatility {nifty.get('volatility', 0):.1f}%, "
            f"max drawdown {nifty.get('max_drawdown', 0):.1f}%\n"
            f"• GOLD: {gold_cagr:.1f}% CAGR, volatility {gold.get('volatility', 0):.1f}%\n\n"
            f"Equities tend to outperform gold over long horizons but with higher drawdowns. "
            f"A small gold allocation (10-15%) acts as a hedge against equity declines and inflation."
        )

    def _answer_stock(self, msg: str) -> str:
        # Detect a stock symbol mention
        symbols = {
            "reliance": "RELIANCE", "tcs": "TCS", "infosys": "INFY",
            "hdfc": "HDFCBANK", "icici": "ICICIBANK", "sbi": "SBIN",
            "itc": "ITC", "airtel": "BHARTIARTL", "wipro": "WIPRO",
            "axis": "AXISBANK", "maruti": "MARUTI",
        }
        symbol = None
        for key, val in symbols.items():
            if key in msg:
                symbol = val
                break
        if not symbol:
            return "I can analyze Indian stocks like RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, SBIN, ITC, etc. Ask e.g. 'Should I buy Reliance?'"
        tech = technical_analyzer.analyze(symbol)
        if not tech.get("available"):
            return f"No technical data available for {symbol}."
        analysis = analytics_engine.analyze(symbol, "5y")
        return (
            f"{symbol} analysis (real market data):\n\n"
            f"• Current price: ₹{tech['current_price']:.2f}\n"
            f"• RSI: {tech['rsi']:.1f} ({self._rsi_label(tech['rsi'])})\n"
            f"• Trend: {tech['trend']}\n"
            f"• Signal: {tech['signal']}\n"
            f"• Support: ₹{tech['support']:.2f}, Resistance: ₹{tech['resistance']:.2f}\n"
            f"• 5Y CAGR: {analysis.get('cagr', 0):.1f}%, Volatility: {analysis.get('volatility', 0):.1f}%\n"
            f"• PE: {analysis.get('pe_ratio', 'N/A')}, Dividend yield: {analysis.get('dividend_yield', 'N/A')}\n\n"
            f"Overall, the signal is {tech['signal']}. "
            f"{'The stock shows positive momentum and may be worth accumulating in tranches.' if tech['signal'] == 'Buy' else 'Consider waiting for better entry or accumulating gradually.' if tech['signal'] == 'Sell' else 'Hold existing positions and watch for a clear trend break.'}"
        )

    def _answer_retirement(self, msg: str, context: Dict[str, Any]) -> str:
        # Extract age if present
        age_match = re.search(r"(?:age|retire at|retire by)\s+(\d{2})", msg.lower())
        age = int(age_match.group(1)) if age_match else 60
        retirement_age = int(age_match.group(1)) if age_match else 45
        months_to_retirement = max((retirement_age - age) * 12, 1)
        income = context["monthly_income"]
        savings = context["monthly_savings"] or income * 0.2
        target_corpus = income * 12 * 25  # 25x rule

        proj = self.projector.project(
            monthly_sip=savings * 0.6,
            years=max(months_to_retirement // 12, 1),
            expected_return=12.0,
            inflation_rate=6.0,
        )
        future_value = proj["future_value"]
        return (
            f"Retirement planning (using your real income ₹{income:.0f}/mo):\n\n"
            f"Assuming you want to retire at {retirement_age}, a common rule is to build "
            f"a corpus of ~25x annual expenses (~₹{target_corpus:.0f}).\n"
            f"With a monthly SIP of ₹{savings * 0.6:.0f} at ~12% CAGR, your projected corpus "
            f"after {months_to_retirement // 12} years is ₹{future_value:.0f} "
            f"({proj['inflation_adjusted_value']:.0f} in today's rupees).\n\n"
            f"To speed this up, consider: 1) Increasing SIP by 10% each year, "
            f"2) Using tax-advantaged options (PPF/NPS/ELSS), 3) Maintaining 60-70% equity "
            f"allocation while you have 15+ years to go."
        )

    def _answer_wealth(self, msg: str, context: Dict[str, Any]) -> str:
        sip = 10000.0
        # Extract amount
        amount_match = re.search(r"₹?\s?([\d,]+)\s*(?:per\s*month|/mo|monthly)", msg.lower())
        if amount_match:
            sip = float(amount_match.group(1).replace(",", ""))
        years = 5
        years_match = re.search(r"(\d+)\s*(?:years|yrs|year)", msg.lower())
        if years_match:
            years = int(years_match.group(1))

        # Use Nifty 50 real CAGR as expected return
        cagr = 12.0
        df = analytics_engine.get_history("NIFTY 50", "5y")
        if not df.empty:
            cagr = analytics_engine.compute_cagr(df)

        proj = self.projector.project(
            monthly_sip=sip, years=years, expected_return=cagr, inflation_rate=6.0
        )
        return (
            f"Wealth projection (real Nifty 50 5Y CAGR of ~{cagr:.1f}%):\n\n"
            f"Investing ₹{sip:.0f}/month for {years} years:\n"
            f"• Total invested: ₹{proj['total_invested']:.0f}\n"
            f"• Expected future value: ₹{proj['future_value']:.0f}\n"
            f"• Total gain: ₹{proj['total_gain']:.0f}\n"
            f"• Inflation-adjusted value: ₹{proj['inflation_adjusted_value']:.0f}\n\n"
            f"Note: These projections are directionally accurate but assume the historical "
            f"CAGR continues. Actual returns vary (10th/90th percentile: ₹{proj['p10']:.0f} / ₹{proj['p90']:.0f})."
        )

    def _answer_health(self, context: Dict[str, Any]) -> str:
        health = context["financial_health"]
        score = health["overall_score"]
        suggestions = health["suggestions"][:3]
        sugg_str = "\n".join(f"{i+1}. {s}" for i, s in enumerate(suggestions))
        return (
            f"Your Financial Health Score is {score:.0f}/100 ({health['category']}).\n\n"
            f"{health['summary']}\n\n"
            f"Top suggestions to improve:\n{sugg_str}"
        )

    def _answer_budget(self, context: Dict[str, Any]) -> str:
        income = context["monthly_income"]
        expense = context["monthly_expense"]
        savings = context["monthly_savings"]
        ratio = context["savings_ratio"]
        return (
            f"Budget analysis (your real data):\n\n"
            f"• Income: ₹{income:.0f}/mo\n"
            f"• Expenses: ₹{expense:.0f}/mo\n"
            f"• Savings: ₹{savings:.0f}/mo ({ratio:.1f}%)\n\n"
            f"Using the 50-30-20 rule, aim for 50% needs, 30% wants, 20% savings. "
            f"You're currently saving {ratio:.1f}%. "
            f"{'Great job! Consider automating investments with the surplus.' if ratio >= 20 else 'Try to cut discretionary spending to reach a 20% savings rate.'}"
        )

    def _answer_market(self) -> str:
        overview = market_analysis_service.market_overview()
        lines = []
        for asset in overview["assets"]:
            lines.append(
                f"• {asset['name']}: ₹{asset['current_price']:.0f} | "
                f"5Y CAGR {asset['cagr']:.1f}% | Vol {asset['volatility']:.1f}% | "
                f"Max DD {asset['max_drawdown']:.1f}%"
            )
        market_str = "\n".join(lines)
        top = overview["top_performing"][:3]
        top_str = "\n".join(f"• {a['name']}: {a['cagr']:.1f}% CAGR" for a in top)
        return (
            f"Market Overview (5-year real data):\n\n{market_str}\n\n"
            f"Top performing stocks:\n{top_str}\n\n"
            f"Markets reward long-term investors, but be mindful of drawdowns. "
            f"Diversify across asset classes."
        )

    def _answer_greeting(self) -> str:
        return (
            "Hello! I'm your AI Financial Advisor. I now use real market data and "
            "your financial records to give personalized advice.\n\n"
            "I can help you with:\n"
            "• Investment planning & SIP calculators\n"
            "• Stock analysis (Should I buy Reliance?)\n"
            "• FD vs Mutual Fund comparisons\n"
            "• Retirement planning\n"
            "• Wealth projections (₹10,000/mo for 5 years)\n"
            "• Financial health & budgeting\n"
            "• Market trends (Nifty, Gold, Sensex)\n\n"
            "What would you like to explore?"
        )

    def _answer_general(self, context: Dict[str, Any]) -> str:
        return (
            "I can help with investments, stock analysis, mutual funds, FD comparisons, "
            "retirement planning, wealth projections, budgeting, and market trends. "
            "Try asking:\n"
            "• 'Where should I invest ₹10,000/month?'\n"
            "• 'Should I buy Reliance?'\n"
            "• 'Compare FD vs Mutual Fund'\n"
            "• 'Can I retire in 10 years?'"
        )

    def _rsi_label(self, rsi: float) -> str:
        if rsi >= 70:
            return "Overbought"
        if rsi <= 30:
            return "Oversold"
        return "Neutral"

    def _sip_future_value(self, monthly: float, years: int, annual_return: float) -> float:
        monthly_rate = (1 + annual_return / 100) ** (1 / 12) - 1
        months = years * 12
        fv = monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
        return fv
