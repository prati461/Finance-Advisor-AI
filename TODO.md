# Finance Advisor AI - Implementation TODO

## Phase 1: Backend Market Data Service + Gemini Integration
- [x] Read and understand existing project structure
- [x] Create TODO.md
- [x] Create `backend/market/` package (base, yahoo_provider, manager, cache)
- [x] Add market data dependencies to `requirements.txt`
- [x] Add Gemini/OpenAI LLM client (`backend/ml/llm/client.py`)
- [x] Add GEMINI_API_KEY / ALPHA_VANTAGE_API_KEY to settings + `.env.example`
- [x] Verify Python files compile

## Phase 2: AI Investment Engine + Chatbot
- [x] Create analytics engine (metrics, technical, sectors, analysis)
- [x] Upgrade `investment_advisor.py` to use real CAGRs + user profile
- [x] Upgrade `portfolio.py` to use real expected returns/volatility
- [x] Upgrade `stock_predictor.py` with XGBoost + indicators + Buy/Hold/Sell
- [x] Create `mutual_fund_service.py`
- [x] Create `wealth_projection.py`
- [x] Replace rule-based `chatbot.py` with Gemini + analytics fallback
- [x] Expand `schemas/ai.py` with new schemas
- [x] Expand `backend/api/v1/ai.py` + new market endpoints

## Phase 3: Charts + Frontend Integration
- [x] Extend `frontend/src/types/index.ts`
- [x] Extend `frontend/src/services/ai.service.ts`
- [x] Extend `frontend/src/hooks/useAI.ts`
- [x] Create chart components (Recharts)
- [x] Create new pages (MarketAnalysis, MutualFund, WealthProjection)
- [x] Add routes + sidebar items

## Phase 4: Testing & Bug Fixes
- [x] Install backend deps
- [x] Run backend, test endpoints
- [x] Run frontend build
- [x] Fix all errors (ChatResponse `source` field, MarketAnalysis page field alignment)
- [x] Verify real market data flows (NIFTY CAGR 8.69%, GOLD 19.59%, RELIANCE technical: Hold/RSI 44.95)
- [x] Verify LLM graceful fallback works when no GEMINI_API_KEY is set
- [x] Verify auth protection + live market-overview endpoint
- [x] Verify mutual fund analysis (real CAGR, pros/cons, recommendation)
- [x] Create `.env.example` with GEMINI_API_KEY / ALPHA_VANTAGE_API_KEY / config
- [x] Final README update + `.env.example` verification

## Fix: Investment Advisor Expected Annual Return (939% -> real)
- [x] Root cause: `_compute_portfolio_return` multiplied by 100 twice
  (`sum(weight*cagr/100) * 100` inflated ~9.4% to ~939%)
- [x] Fixed: weighted sum = `sum(weight_pct * cagr_pct / 100)`, no extra *100
- [x] Added debug logging (asset, allocation %, historical CAGR, weighted contribution, final %)
- [x] Verified all 5 risk profiles: Conservative 9.53%, Cons-Mod 9.86%, Moderate 9.58%,
      Mod-Agg 9.39%, Aggressive 8.41% — all match hand-check, realistic 3–25%
- [x] Wealth projection now uses corrected ~9–10% return (realistic 5-yr values)
