---
name: kryptogo-meme-trader
version: "2.4.3"
description: Analyze and trade meme coins using KryptoGO's on-chain cluster analysis platform. Covers wallet clustering, address labels, accumulation/distribution detection, and automated swap execution via the Agent Trading API.
author: KryptoGO
license: MIT
homepage: https://www.kryptogo.xyz
tags:
  - solana
  - trading
  - meme-coins
  - defi
  - agent-trading
  - on-chain-analysis
  - cluster-analysis
  - kryptogo
platform: solana
api_base: https://wallet-data.kryptogo.app
metadata:
  openclaw:
    requires:
      env:
        - KRYPTOGO_API_KEY
        - SOLANA_PRIVATE_KEY
        - SOLANA_WALLET_ADDRESS
      bins:
        - python3
        - pip
        - openclaw
      network:
        - wallet-data.kryptogo.app
      permissions:
        - filesystem:write:~/.openclaw/workspace/.env
        - filesystem:write:~/.openclaw/workspace/memory/
      runtime_installs:
        - "pip: solders, requests (installed by scripts/setup.py on first run)"
      primaryEnv: KRYPTOGO_API_KEY
---

# KryptoGO Meme Trader Agent Skill

## Overview

This skill enables an AI agent to **autonomously analyze and trade** meme coins through the KryptoGO platform. It combines deep on-chain cluster analysis with automated trade execution.

**Analysis** (multi-chain: Solana, BSC, Base, Monad):
- Wallet clustering — identify entities controlling multiple addresses
- Accumulation/distribution detection — who's buying vs. selling
- Address behavior labels — smart money, whales, snipers, developers
- Network-wide accumulation signals (Pro/Alpha tier)

**Trading** (Solana only):
- Portfolio monitoring with per-token PnL tracking
- Automated swap execution via DEX aggregator
- Local transaction signing (private key never leaves the machine)

**Important:** Analysis supports Solana, BSC, Base, and Monad. Trading (swap/submit) is Solana-only.

**Workflow:** discover signal → analyze token → assess risk → execute trade → monitor position.

---

## When to Use

- User asks to analyze a meme coin or token on Solana/BSC/Base/Monad
- User asks to trade, buy, or sell tokens
- User asks to scan for trending tokens or market opportunities
- User asks to monitor portfolio positions or check PnL
- Heartbeat/cron-triggered periodic portfolio monitoring and signal scanning
- Pro/Alpha subscribers leveraging signal dashboard for curated accumulation signals

## When NOT to Use

- BTC, ETH, or major L1 token macro analysis (not meme-specific)
- NFT-related questions
- Cross-chain bridging or non-DEX transactions
- General crypto news or price predictions without on-chain analysis
- Non-Solana trading execution

---

## Setup Flow

### 1. Get API Key

1. Go to [kryptogo.xyz/account](https://www.kryptogo.xyz/account) and create an API key
2. Add it to `~/.openclaw/workspace/.env` (the workspace root `.env`):
   ```bash
   echo 'KRYPTOGO_API_KEY=sk_live_YOUR_KEY' >> ~/.openclaw/workspace/.env && chmod 600 ~/.openclaw/workspace/.env
   ```
3. Tell the agent "I've set my API key in .env" — the agent will verify it works by calling `/agent/account`

> **Do NOT paste your API key directly in chat.** Chat histories may be stored and could expose your key. Always set secrets via `.env` file or environment variables.
>
> All credentials are stored in `~/.openclaw/workspace/.env` — the OpenClaw workspace root. This ensures heartbeat/cron sessions can find them automatically.
>
> The API key is tied to your KryptoGO account (for billing/tier), NOT to a specific wallet.
> Your login wallet on kryptogo.xyz may differ from the agent's trading wallet.

### 2. Generate Agent Wallet

Run the setup script to create a dedicated Solana keypair:

```bash
python3 scripts/setup.py
```

This will:
1. Check Python 3.10+ and install `solders` + `requests` if missing
2. Generate a new Solana keypair
3. Save the private key (base58) and public address to `~/.openclaw/workspace/.env`
4. Set `.env` permissions to 600 (owner read/write only)
5. Print the public address for the user to fund with SOL

### 3. Fund the Wallet

Send SOL to the agent's public address (minimum 0.1 SOL for gas + trading capital).

### Security Rules

- **NEVER** print, log, or include the private key in any message or CLI argument
- **NEVER** accept secrets (API keys, private keys) pasted directly in chat — instruct users to set them in `.env`
- **NEVER** commit `.env` to version control
- **NEVER** use the Read tool on `~/.openclaw/workspace/.env` — load credentials via `source` command only, which doesn't expose values in tool output
- The private key stays in memory only during local signing — it is never sent to any server
- `.env` must always have chmod 600
- See [Safety Guardrails](#safety-guardrails) for full credential handling and trading limits

### Quickstart Checklist

After installing this skill, complete these steps in order:

1. [ ] Get API key from [kryptogo.xyz/account](https://www.kryptogo.xyz/account) and add it to `.env`
2. [ ] Run `python3 scripts/setup.py` to generate agent wallet
3. [ ] Fund the agent wallet with SOL (min 0.1 SOL)
4. [ ] Tell the agent your trading preferences (max position size, risk tolerance, etc.)
5. [ ] Set up automated monitoring — run `bash scripts/cron-examples.sh setup-default` or see [Automated Monitoring (Cron)](#automated-monitoring-cron)

---

## Authentication

All endpoints require Bearer token authentication:

```
Authorization: Bearer sk_live_<48 hex chars>
```

Some features (signal dashboard, KOL finder) additionally require Pro or Alpha tier subscription.

| Tier  | Daily API Calls | Trading Fee | Signal Dashboard | KOL Finder |
|-------|-----------------|-------------|------------------|------------|
| Free  | 50 calls/day    | 1%          | No               | No         |
| Pro   | 500 calls/day   | 0.5%        | Yes              | Yes        |
| Alpha | 5,000 calls/day | 0%          | Yes              | Yes        |

---

## Agent Behavior

### Session Initialization

On every session start (including heartbeat/cron), the agent MUST load credentials before making any API calls:

```bash
source ~/.openclaw/workspace/.env
```

This makes `KRYPTOGO_API_KEY`, `SOLANA_PRIVATE_KEY`, and `SOLANA_WALLET_ADDRESS` available as environment variables. Do NOT use the Read tool on `.env` — the `source` command loads values without exposing them in tool output.

### Autonomous Mode (Default)

**Automatic actions (no user confirmation needed):**
- Scanning trending tokens (default: top 10 per scan)
- Running full analysis pipeline on candidate tokens
- Checking portfolio status and PnL
- Executing trades that pass ALL criteria in the Bullish Checklist
- Stop-loss sells when unrealized loss exceeds threshold
- Take-profit sells when gain exceeds target

**Requires user confirmation:**
- Risk level is "medium" (ambiguous signals)
- Position size exceeds user-defined max
- Selling at a loss outside stop-loss rules
- Any action outside the defined entry/exit strategies

**Reporting:**
- After each trade: summarize analysis result + trade details to the user (concise text, not raw JSON)
- After each scan: brief summary of tokens scanned, why they passed/failed
- On errors: report the issue and suggest next steps

### Persistence (CRITICAL)

**IMMEDIATELY after submitting a transaction, the agent MUST:**
1. **Write the trade details to `memory/trading-journal.json`** with `status: "OPEN"`.
   - Include: `token_symbol`, `token_address`, `entry_price`, `position_size_sol`, `tx_hash`, `timestamp`.
   - **Do not wait for confirmation** — write it as soon as `tx_hash` is obtained.
2. If this step is skipped, the Stop-Loss cron job will NOT see the position and will fail to manage it.

### User Preferences

The user can customize behavior by telling the agent their preferences. Store in `memory/trading-preferences.json`:

```json
{
  "max_position_size": 0.1,
  "max_open_positions": 5,
  "max_daily_trades": 20,
  "stop_loss_pct": 30,
  "take_profit_pct": 100,
  "min_market_cap": 500000,
  "scan_count": 10,
  "risk_tolerance": "moderate",
  "chains": ["solana"]
}
```

| Preference | Default | Description |
|------------|---------|-------------|
| `max_position_size` | 0.1 SOL | Max SOL per trade |
| `max_open_positions` | 5 | Max concurrent open positions |
| `max_daily_trades` | 20 | Max trades per day (buys + sells) |
| `stop_loss_pct` | 30% | Auto-sell when loss exceeds this |
| `take_profit_pct` | 100% | Auto-sell when gain exceeds this |
| `min_market_cap` | $500K | Skip tokens below this market cap |
| `scan_count` | 10 | Number of trending tokens per scan |
| `risk_tolerance` | "moderate" | "conservative" (skip medium risk), "moderate" (ask on medium), "aggressive" (auto-trade medium) |
| `chains` | ["solana"] | Chains to scan for analysis |

---

## Safety Guardrails

This skill handles real funds. These guardrails limit blast radius if credentials are mishandled or the agent malfunctions.

### Credential Isolation

- **API key and private key are stored ONLY in `~/.openclaw/workspace/.env`** with chmod 600 (owner read/write)
- The agent reads credentials via environment variables (`source ~/.openclaw/workspace/.env`) — they are **never** printed, logged, passed as CLI arguments, or included in chat messages
- The agent must **never** use the Read tool on `.env` — the `source` command keeps values out of tool output
- If a user pastes a secret in chat, the agent should warn them and suggest rotating it

### Trading Limits (Hard Caps)

These limits apply even if user preferences set higher values:

| Limit | Default | Can User Override? |
|-------|---------|--------------------|
| Max single trade | 0.1 SOL | Yes, via `max_position_size` in preferences |
| Max concurrent positions | 5 | Yes, via `max_open_positions` (default: 5) |
| Max daily trade count | 20 | Yes, via `max_daily_trades` (default: 20) |
| Price impact abort | >10% | No — always abort |
| Price impact warn | >5% | No — always warn user |

If any limit is hit, the agent **must stop and notify the user** — never silently skip.

### Autonomous Trading Scope

- The agent **only** executes trades that pass ALL criteria in the Bullish Checklist (Step 6)
- Ambiguous signals (risk = "medium") **always** require user confirmation
- The agent **cannot** modify its own trading parameters — only propose changes for user approval
- All trade executions are **immediately reported** to the user via the configured channel (Telegram, Discord, etc.)

### Kill Switch

See [Automated Monitoring — Kill Switch](#kill-switch) for how to stop all autonomous trading.

### Audit Trail

Every action is logged to `memory/` files (see [Learning Memory Files](#learning-memory-files)):
- `trading-journal.json` — complete trade history with reasoning
- `trading-state.json` — current positions and last scan time
- `trading-lessons.md` — post-mortem analysis

These files are human-readable and can be reviewed at any time.

---

## Automated Monitoring (Cron)

The recommended setup uses **two OpenClaw cron jobs** working together:

| Job | Interval | Purpose |
|-----|----------|---------|
| `stop-loss-tp` | Every **5 min** | Check portfolio, execute stop-loss / take-profit |
| `discovery-scan` | Every **30 min** | Discover new tokens, analyze, and auto-buy qualifying ones |

This separation ensures time-sensitive exit orders run frequently, while the heavier discovery + analysis pipeline runs at a sustainable pace.

### Default Setup (Recommended)

Run this to install both cron jobs:

```bash
bash scripts/cron-examples.sh setup-default
```

Or add them manually:

```bash
# Job 1: Stop-loss / Take-profit — every 5 minutes
openclaw cron add \
  --every 5m \
  --name "stop-loss-tp" \
  --prompt "Load the kryptogo-meme-trader skill. Source .env. Call /agent/portfolio with the agent wallet.
For each open position:
- If unrealized PnL ≤ -stop_loss_pct → sell entire position (stop-loss).
- If unrealized PnL ≥ +take_profit_pct → sell entire position (take-profit).
Read thresholds from memory/trading-preferences.json (defaults: stop_loss_pct=30, take_profit_pct=100).
Report every executed trade to the user. If no action taken, stay silent."

# Job 2: Discovery & Analysis — every 30 minutes
openclaw cron add \
  --every 30m \
  --name "discovery-scan" \
  --prompt "Load the kryptogo-meme-trader skill. Source .env. Execute the full discovery workflow:
1. Read memory/trading-preferences.json for current parameters.
2. Read memory/trading-lessons.md (if exists) to avoid known bad patterns.
3. Check open positions count — skip buying if at max_open_positions.
4. Scan for candidates:
   - Pro/Alpha tier: call /signal-dashboard (sort_by=signal_count, page_size=10).
   - Free tier: call /agent/trending-tokens with min_market_cap filter.
5. Run top candidates through the 7-step analysis pipeline.
6. For tokens passing ALL criteria in the Bullish Checklist: execute buy with max_position_size.
   For 'medium' risk: ask user for confirmation (unless risk_tolerance='aggressive').
7. Log any new trades to memory/trading-journal.json.
8. Update memory/trading-state.json with scan timestamp.
9. If any trades were closed since last scan: run post-trade reflection and update trading-lessons.md.
10. If 20+ trades or 7+ days since last review: trigger Strategy Review.
Report ALL actions to the user. If nothing happened, stay silent."
```

### Quick Commands

```bash
# List active cron jobs
openclaw cron list

# Pause trading (remove both jobs)
openclaw cron remove stop-loss-tp
openclaw cron remove discovery-scan

# Resume trading
bash scripts/cron-examples.sh setup-default
```

### First-Time Auto-Setup (Agent Instruction)

The first time this skill is loaded in a conversation, check if the `stop-loss-tp` and `discovery-scan` cron jobs already exist (via `openclaw cron list`). If not, **proactively offer to set them up** — ask the user: "I can set up automated stop-loss (every 5 min) and discovery scanning (every 30 min). Want me to add these cron jobs?" If confirmed, run `bash scripts/cron-examples.sh setup-default`.

### Alternative: Heartbeat-Based Monitoring

If you prefer a simpler setup (one check every ~30 min instead of two separate cron jobs), add this to `HEARTBEAT.md`:

```markdown
## Trading Agent
- Check portfolio: call /agent/portfolio, execute stop-loss/take-profit if triggered
- Scan for opportunities: use signal dashboard (Pro/Alpha) or trending tokens API
- Execute qualifying trades in autonomous mode
- Log closed trades to journal, run post-trade reflection, trigger strategy review if due
- ALWAYS report any trade executed to the user — never silent HEARTBEAT_OK after trading
```

**Tradeoff:** Heartbeat batches everything into one turn (~30 min intervals). This means stop-loss could be delayed up to 30 minutes. Use cron if you need faster exit execution.

### Monitoring Workflow

1. **Portfolio check** (every 5 min via `stop-loss-tp`)
   - Execute stop-loss if unrealized loss > `stop_loss_pct`
   - Execute take-profit if unrealized gain > `take_profit_pct`
   - Flag stale positions (held > 7 days with no significant movement)
2. **Signal scan** (every 30 min via `discovery-scan`)
   - **Pro/Alpha tier:** Use `/signal-dashboard` first — these are system-curated accumulation signals (clusters actively buying). Higher quality than raw trending lists because they're pre-filtered for smart money activity. Parameters: `chain_id`, `sort_by=signal_count`, `page_size=10`.
   - **Free tier:** Fall back to `/agent/trending-tokens` with filters (`min_market_cap`, `min_liquidity`, etc.)
   - Run top results through the 7-step analysis pipeline
   - Auto-trade if all criteria pass; ask user if risk = "medium"
3. **State persistence** → Save to `memory/trading-state.json`
   - Tracks: last scan time, open positions, pending user reviews
   - On next scan, read this file to resume state
4. **Learning check** → If any trades were closed since last check:
   - Log outcome to `memory/trading-journal.json`
   - Run post-trade reflection (mandatory for every closed trade)
   - If loss >20%, trigger Loss Post-Mortem
   - If 20+ trades accumulated or 7+ days since last review, trigger Strategy Review

### Notification Rules

**Mandatory — agent MUST message the user when:**
- Any trade is executed (buy or sell)
- A stop-loss or take-profit is triggered
- A position is flagged for manual review (medium risk, stale, etc.)
- An error prevents normal operation (API down, insufficient SOL, quota exceeded)

**Stay silent when:**
- Portfolio checked, no action needed
- Tokens scanned, none qualified
- Everything nominal

### Kill Switch

To immediately stop all autonomous trading:
1. **Remove cron jobs:** `openclaw cron remove stop-loss-tp && openclaw cron remove discovery-scan`
2. **Remove Trading Agent section from HEARTBEAT.md** (if using heartbeat mode)
3. **Remove or rename `.env`** — prevents any API calls or signing

The agent has no persistence mechanism beyond cron entries and HEARTBEAT.md. Removing those stops all autonomous behavior.

### Failure Recovery

If the agent crashes or session ends mid-trade:
- On startup, **ALWAYS** call `/agent/portfolio` first to check current holdings
- Compare with `memory/trading-state.json` to detect any untracked positions
- Report any discrepancies to the user immediately

---

## On-Chain Analysis Framework (7-Step Pipeline)

### Step 1: Token Overview & Market Cap Filter

Call `/token-overview?address=<mint>&chain_id=<id>` — get name, price, market cap, holders, risk_level, liquidity.

**Filter:** Skip if market cap < user's `min_market_cap`.

**Early filtering from signal data:** When tokens come from `/signal-dashboard` or `/agent/trending-tokens`, the response already includes `current_price` and `total_supply`. You can compute `market_cap ≈ current_price * total_supply` immediately — no need to call `/token-overview` just for the first-pass market cap filter. This saves API calls on tokens that will be discarded anyway.

**Preferences integration:** Always read `memory/trading-preferences.json` first and apply `min_market_cap` at the signal level before entering the full pipeline.

### Step 2: Cluster Analysis

Call `/analyze/<mint>?chain_id=<id>` — get wallet clusters, top holders, address metadata.

**Key metric — Cluster Holding Ratio:**
- ≥30-35% = "controlled" — a major entity holds significant supply
- ≥50% = highly concentrated — high manipulation risk
- <10% = dispersed — no clear major holder

**Scam rule:** If a SINGLE cluster holds >50% of supply → skip (rug pull risk).

### Step 3: Cluster Trend (Multi-Timeframe)

Call `/analyze-cluster-change/<mint>` — get `cluster_ratio` and `changes` across 15m/1h/4h/1d/7d.

**Core insight:** Price and cluster holdings DIVERGING is the most important signal.
- Rising price + falling cluster % = distribution (bearish)
- Falling price + rising cluster % = accumulation (bullish)

**Multi-timeframe interpretation:**

| Timeframe | Purpose | Example |
|-----------|---------|---------|
| **7d** | Long-term trend — sustained accumulation vs. sustained distribution | 7d > 0 = week-long buying; 7d < 0 = week-long selling |
| **1d** | Recent re-accumulation — did the entity start buying again? | 1d > 0 after 7d < 0 = potential reversal |
| **4h** | Mid-term distribution detection | 4h < -5% = consider reducing or skipping entry |
| **15m / 1h** | Short-term timing — wash trading, consolidation, or knife-catching | Used for entry timing, not for conviction |

**Read together:** A token with 7d slightly negative but 1d positive suggests "mid-term correction followed by re-accumulation" — often a good entry if other signals align.

### Step 4: Address Labels + Sell Pressure Verification

Call `/token-wallet-labels` for token-specific labels (developer, sniper, bundle, new_wallet).
Call `/wallet-labels` for behavior labels (smart_money, whale, blue_chip_profit, high_frequency).

> **Critical rule:** Labels represent *behavioral history*, not current holdings. Any risk judgment MUST be combined with `/balance-history` to check current balances.

**Correct flow for assessing dev/sniper/bundle risk:**

1. **Get labeled addresses** — call `/token-wallet-labels` to identify wallets tagged as `developer`, `sniper`, or `bundle`.
2. **Check current balance** — for each risky address, call `/balance-history` with the specific `token_mint`:
   - Look at the most recent balance entry.
   - If balance ≈ 0 → the address has **exited** — do NOT count as risk.
   - If balance is still significant → this is a **potential dump source**.
3. **Compute risky holding ratio:**
   ```
   risky_ratio = (sum of tokens held by active dev/sniper/bundle wallets) / (total cluster holdings)
   ```
4. **Classify risk level:**
   - `risky_ratio > 30%` → **high** — skip or require user confirmation
   - `risky_ratio 10%–30%` → **medium** — proceed with caution
   - `risky_ratio < 10%` → **low** — risk addresses have largely exited

**Common mistake (do NOT do this):** Seeing `developer` or `sniper` labels and immediately marking the token as "HIGH RISK" without checking balances. Many risky addresses sell early and have zero balance by the time you analyze.

### Step 5: Deep Dive (Optional)

- `/balance-history` — time-series balance for specific wallets
- `/balance-increase/<mint>` — who bought most in a time range
- `/top-holders-snapshot/<mint>` — point-in-time holder snapshot
- `/analyze-dca-limit-orders/<mint>` — DCA/limit order detection (Solana only)
- `/cluster-wallet-connections` — fund flow between wallets

**Holding Trend Analysis** — For a deeper conviction check, combine multiple API calls to track how key groups' holdings change over time as a percentage of total supply:

1. Get `total_supply` from `/token-overview`
2. Extract cluster wallet addresses and smart money addresses from `/analyze/<mint>`
3. Call `/balance-history` with those wallets aggregated to get daily balances
4. Compute `(balance / total_supply) * 100` for each day

This reveals whether clusters and smart money are **steadily accumulating** (bullish) or **gradually distributing** (bearish) — a more granular signal than the snapshot cluster ratio from Step 2.

> See `examples/deep-analysis-workflow.py` for a complete Python implementation of this technique.

### Step 6: Decision

Apply the Bullish Checklist from the Decision Framework:
- Market cap ≥ user's `min_market_cap`
- Cluster ratio ≥ 30% and rising
- Smart money/whale clusters increasing
- Developer/sniper/bundle positions cleared (verified via `/balance-history`, not just labels)
- No high proportion of new wallets or high-frequency traders

> Full decision framework: see `references/decision-framework.md`

**Example: "Buy" decision (template)**

A token with these characteristics is a reasonable entry with `max_position_size`:

| Factor | Value | Assessment |
|--------|-------|------------|
| Market cap | ~$500K | ≥ min_market_cap |
| Liquidity | ~$170K | Sufficient for position size |
| Cluster ratio | ~31% | Controlled — major entity present |
| 1d cluster change | > 0 | Recent re-accumulation |
| 7d cluster change | Slightly negative | Prior distribution phase ended |
| Dev/sniper/bundle | All exited (balance ≈ 0 via `/balance-history`) | No active dump risk |
| Conclusion | **Mid-correction re-accumulation** — acceptable risk for trial position using `max_position_size` |

### Step 7: Execute Trade

**CRITICAL: Use `python3 scripts/swap.py` for execution whenever possible.**
It automatically handles `wallet_address` injection, error checking, and **mandatory journal logging**.

If you must implement custom logic:
1. `POST /agent/swap` with `wallet_address` set to your agent's `SOLANA_WALLET_ADDRESS` — builds an unsigned transaction with that address as fee payer / signer
2. **Verify before signing:** decode the unsigned tx and confirm `fee_payer` in the response matches your wallet
3. Sign locally with `solders` (private key never sent to server)
4. `POST /agent/submit` — submit signed transaction
5. Verify via explorer URL
6. **IMMEDIATELY write to trading journal** (see Persistence section).

> **Important:** Always pass `wallet_address` in the swap request. Without it, the API uses the wallet associated with your API key (which may differ from your agent's trading wallet), causing a signer mismatch when you try to sign locally.

> Full trading workflow: see `examples/trading-workflow.py`

---

## API Quick Reference

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/agent/account` | GET | Yes | Check tier & quota |
| `/agent/trending-tokens` | GET | Yes | Scan trending tokens with filters |
| `/agent/portfolio` | GET | Yes | Wallet portfolio + PnL |
| `/agent/swap` | POST | Yes | Build unsigned swap tx (Solana only) |
| `/agent/submit` | POST | Yes | Submit signed tx (Solana only) |
| `/token-overview` | GET | Yes | Token metadata & market data |
| `/analyze/:token_mint` | GET | Yes | Full cluster analysis |
| `/analyze-cluster-change/:token_mint` | GET | Yes | Cluster ratio trends |
| `/balance-history` | POST | Yes | Time-series balance data |
| `/wallet-labels` | POST | Yes | Behavior labels (smart money, whale...) |
| `/token-wallet-labels` | POST | Yes | Token-specific labels (dev, sniper...) |
| `/signal-dashboard` | GET | Pro+ | **Curated accumulation signals — prefer this over trending tokens when available** |
| `/balance-increase/:token_mint` | GET | Yes | Range accumulation filter |
| `/top-holders-snapshot/:token_mint` | GET | Yes | Point-in-time holder snapshot |
| `/historical-top-holders/:token_mint` | GET | Yes | All-time top holders |
| `/fresh-addresses/:token_mint` | GET | Yes | New wallet holders (Solana only) |
| `/analyze-dca-limit-orders/:token_mint` | GET | Yes | DCA & limit order detection (Solana only) |
| `/price-chart` | GET | No | OHLCV candlestick data |
| `/batch-token-prices` | POST | No | Batch price lookup |
| `/cluster-wallet-connections` | POST | Yes | Fund flow between wallets |
| `/wallet-assets` | GET | Yes | Wallet token holdings |
| `/signal-history/:address` | GET | Yes | Historical signals for token |

> Full request/response details: see `references/api-reference.md`

---

## Multi-Chain Support

| Chain | chain_id | Address Format | Analysis | Trading |
|-------|----------|----------------|----------|---------|
| Solana | `501` (default) | Base58 | Yes | Yes |
| BSC | `56` | Hex (0x-prefixed) | Yes | No |
| Base | `8453` | Hex (0x-prefixed) | Yes | No |
| Monad | `143` | Hex (0x-prefixed) | Yes | No |

Pass `chain_id` as a query parameter on analysis endpoints. Trading endpoints only work with Solana.

---

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad Request | Check parameters |
| 401 | Unauthorized | Check API key |
| 402 | Quota Exceeded | Wait for daily reset or upgrade tier |
| 403 | Forbidden | Endpoint requires higher tier |
| 502 | Bad Gateway | Retry once after 10s |
| 504 | Timeout | Cluster analysis taking too long, retry later |

---

## Learning & Adaptation

The agent improves over time by recording every trade, analyzing outcomes, and adjusting its strategy based on accumulated experience.

### Trade Journal

Every trade (buy or sell) MUST be logged to `memory/trading-journal.json` immediately after execution:

```json
{
  "trades": [
    {
      "id": "2026-02-25T14:30:00Z_BONK",
      "token_mint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
      "symbol": "BONK",
      "chain_id": "501",
      "action": "BUY",
      "amount_sol": 0.1,
      "token_amount": 150000000,
      "price_at_entry": 0.0000234,
      "market_cap_at_entry": 1500000,
      "timestamp": "2026-02-25T14:30:00Z",
      "entry_reasoning": {
        "cluster_ratio": 0.35,
        "cluster_change_1d": 0.05,
        "smart_money_count": 3,
        "dev_exited": true,
        "sniper_cleared": true,
        "signal_source": "signal_dashboard",
        "risk_level": "low"
      },
      "outcome": null
    }
  ]
}
```

When a position is closed (sell), update the corresponding BUY entry's `outcome`:

```json
{
  "outcome": {
    "exit_price": 0.0000468,
    "exit_timestamp": "2026-02-26T09:15:00Z",
    "exit_reason": "take_profit",
    "pnl_sol": 0.1,
    "pnl_pct": 100.0,
    "holding_duration_hours": 18.75,
    "cluster_ratio_at_exit": 0.28,
    "lesson": "Cluster started distributing 2h before exit — could have sold earlier at higher price"
  }
}
```

### Mandatory Post-Trade Reflection

**After every SELL (win or loss), the agent MUST:**

1. Compare the entry reasoning with the actual outcome
2. Identify what the analysis got right and what it missed
3. Write a one-sentence `lesson` in the outcome record
4. If the loss was >20%, do a **Loss Post-Mortem** (see below)

### Loss Post-Mortem

When a trade results in a loss >20%, the agent MUST perform a detailed post-mortem:

1. **Re-run analysis** on the token at current state — what changed since entry?
2. **Identify the miss**: Was it a signal that was there but ignored? An unexpected event? A parameter that was too loose?
3. **Classify the loss type**:
   - `signal_miss` — warning signs existed at entry but weren't weighted enough
   - `timing_error` — analysis was correct but entry/exit timing was wrong
   - `external_event` — unpredictable event (rug pull, exploit, market crash)
   - `parameter_drift` — thresholds were too loose (e.g., accepted low cluster ratio)
   - `overconfidence` — entered despite ambiguous signals
4. **Log to `memory/trading-lessons.md`** with the specific pattern to watch for

### Periodic Strategy Review

**Trigger:** Every 20 trades OR every 7 days (whichever comes first), during a heartbeat/cron cycle.

The agent should:

1. **Calculate aggregate stats** from the journal:
   - Win rate (% of trades with positive PnL)
   - Average win size vs average loss size
   - Best/worst performing entry strategies (signal_dashboard vs trending_tokens)
   - Average holding duration for wins vs losses
   - Most common loss types

2. **Identify patterns**:
   - "Trades entered via signal_dashboard have 65% win rate vs 30% from trending_tokens"
   - "Positions held >24h tend to lose money — meme coins need faster exits"
   - "Tokens with cluster_ratio <25% at entry always lost"

3. **Propose parameter adjustments** to the user:
   - "Based on last 20 trades, I suggest raising `min_market_cap` from $500K to $1M (tokens below $1M had 80% loss rate)"
   - "Stop loss of 30% was never triggered before a 50% drop — consider tightening to 20%"
   - "Take profit at 100% missed several peaks — consider partial exit at 50%"

4. **Save review to `memory/strategy-reviews/YYYY-MM-DD.md`**

5. **Update preferences** only after user approves the proposed changes

### Learning Memory Files

| File | Purpose | Updated |
|------|---------|---------|
| `memory/trading-journal.json` | Every trade with entry reasoning + outcome | After every trade |
| `memory/trading-lessons.md` | Specific patterns learned from losses | After losing trades |
| `memory/strategy-reviews/YYYY-MM-DD.md` | Periodic aggregate analysis | Every 20 trades or 7 days |
| `memory/trading-preferences.json` | Current strategy parameters | When user approves changes |
| `memory/trading-state.json` | Runtime state (open positions, last scan) | After every action |

### Example: Learning in Action

```
Week 1: Agent enters 5 trades using default parameters
  → 2 wins (+80%, +45%), 3 losses (-30%, -25%, -18%)
  → Win rate: 40%, avg win: +62.5%, avg loss: -24.3%

Post-mortem on -30% loss:
  → Token had cluster_ratio 22% at entry (below 30% threshold was relaxed because trending)
  → Lesson: "Never relax cluster_ratio below 25%, even for trending tokens"

Week 2 review:
  → Agent proposes: "Raise min cluster_ratio from 20% to 28%"
  → User approves → preferences updated
  → Agent also notices: "All wins came from signal_dashboard source"
  → Agent proposes: "Allocate 80% of scans to signal_dashboard, 20% to trending"

Week 3: Improved win rate from 40% → 55% with tighter parameters
```

### What the Agent Should NOT Do

- **Never auto-adjust parameters without user approval** — always propose and wait
- **Never delete journal entries** — the full history is needed for pattern analysis
- **Never ignore a post-mortem** — even if the loss was small, the pattern matters
- **Never blame "market conditions"** without specifics — always look for actionable lessons

---

## Best Practices

1. **Always check `/agent/account` first** to confirm tier and remaining quota
2. **Always check `/agent/portfolio` on startup** to detect existing positions
3. **Never expose private keys** in logs, messages, or CLI arguments
4. **Validate price impact** before submitting — abort if >10%, warn if >5%
5. **Sign and submit promptly** — blockhash expires after ~60 seconds
6. **Use stop losses** — meme coins can drop 50%+ in minutes
7. **Persist state** — save trading state to `memory/trading-state.json` after every action
8. **Respect rate limits** — check quota before batch operations
9. **Log every trade to journal** — no exceptions, even failed trades are learning data
10. **Reflect after every exit** — write a lesson, even for wins (what made it work?)
11. **Review and propose, never auto-adjust** — parameter changes require user approval
12. **Read trading-lessons.md before scanning** — avoid repeating known bad patterns

---

## Implementation Notes & Lessons

These are hard-won lessons from real trading attempts. Follow them to avoid known pitfalls.

### 1. Transaction Signer Must Match Your Wallet

Before signing an unsigned transaction locally, **always decode it and verify** that the fee payer / first signer matches your `SOLANA_WALLET_ADDRESS`. If they don't match, the backend did not build the transaction for your wallet — do NOT attempt to sign it.

**Fix:** Always pass `wallet_address` in the `POST /agent/swap` request body.

### 2. `/agent/swap` Supports `wallet_address` Parameter

The swap endpoint accepts an optional `wallet_address` field. When provided:
- The unsigned transaction uses that address as the fee payer and signer
- The response includes `fee_payer` and `signers` fields for client-side verification

Without it, the API defaults to the wallet associated with your API key — which may be a different wallet than the one you're trying to sign with.

### 3. Labels Are History, Not Current State

`/token-wallet-labels` returns behavioral labels (developer, sniper, bundle) based on historical actions. These labels do NOT indicate current holdings. A developer who sold everything 3 days ago still carries the `developer` label.

**Always verify current holdings via `/balance-history`** before making risk decisions based on labels.

### 4. Analysis Pipeline Order Is Mandatory

Never skip to trading without completing analysis. The pipeline order exists to prevent losses:

1. Signal dashboard / trending tokens → candidates
2. Market cap / liquidity / preferences filter → eliminate small/illiquid tokens
3. Cluster multi-timeframe analysis → assess accumulation/distribution
4. Label + `/balance-history` verification → confirm sell pressure is real or not
5. Decision checklist → final go/no-go
6. Swap + sign + submit → execute trade

---

## Core Concepts Quick Reference

| Concept | Key Insight |
|---------|-------------|
| **Cluster** | Group of wallets controlled by same entity, linked by fund flow/timing/transactions |
| **Cluster Ratio** | % of supply held by all clusters. ≥30% = controlled, ≥50% = high risk, <10% = dispersed |
| **Developer** | Deployed the token. Lowest cost basis = highest dump risk |
| **Sniper** | Bought within 1 second of creation. If not cleared = sell pressure |
| **Smart Money** | Realized profit >$100K. Their accumulation often precedes price moves |
| **Accumulation** | Cluster % rising + price consolidating = bullish |
| **Distribution** | Price rising + cluster % falling = bearish |
| **Holding Trend** | Track cluster/smart money balance as % of total supply over time — reveals gradual accumulation/distribution invisible in snapshots |

> Full concepts guide: see `references/concepts.md`

---

## Operational Scripts

Ready-to-run scripts for common trading operations. All scripts load credentials from `~/.openclaw/workspace/.env` automatically.

### Portfolio Check

```bash
bash scripts/portfolio.sh                    # Agent wallet
bash scripts/portfolio.sh <wallet_address>   # Any wallet
```

Shows SOL balance, token holdings, and realized/unrealized PnL.

### Trending Token Scanner

```bash
bash scripts/trending.sh           # Top 10 by volume on Solana
bash scripts/trending.sh 20        # Top 20
bash scripts/trending.sh 10 56     # Top 10 on BSC (chain_id=56)
```

### Full Analysis Dashboard

```bash
bash scripts/analysis.sh
```

Combines portfolio, signal dashboard (Pro/Alpha), trending tokens, and top candidate scoring into a single view. Outputs:
1. Portfolio summary with PnL
2. Active accumulation signals with cluster ratio trends
3. Top 10 trending tokens by volume
4. Top 5 candidates ranked by cluster ratio growth + early-stage picks

### Swap Executor

```bash
# Buy 0.1 SOL worth of a token
python3 scripts/swap.py <token_mint> 0.1

# Sell tokens back to SOL
python3 scripts/swap.py <token_mint> <amount_units> --sell

# Custom slippage (basis points, default: 300 = 3%)
python3 scripts/swap.py <token_mint> 0.1 --slippage 500
```

Handles the full build → local sign → submit flow. Verifies fee payer match, checks price impact (aborts >10%, warns >5%), and prints explorer URL on success.

### API Connectivity Test

```bash
bash scripts/test-api.sh
```

Tests account, trending tokens, portfolio, and signal dashboard endpoints. Reports pass/fail for each.

### Cron Setup

```bash
bash scripts/cron-examples.sh setup-default   # Install recommended dual-cron (5m stop-loss + 30m discovery)
bash scripts/cron-examples.sh teardown         # Remove all trading cron jobs
```

See [Automated Monitoring (Cron)](#automated-monitoring-cron) for full details and alternative strategies.

### Trading Preferences Template

Copy `scripts/trading-preferences.example.json` to `memory/trading-preferences.json` and customize:

```bash
cp scripts/trading-preferences.example.json memory/trading-preferences.json
```

---

## File Structure

```
kryptogo-meme-trader/
├── SKILL.md                       ← You are here (compact overview)
├── .env.example                   ← Environment variable template
├── references/
│   ├── api-reference.md           ← Full API docs with request/response examples
│   ├── concepts.md                ← Core concepts (clustering, labels, accumulation)
│   └── decision-framework.md      ← Entry/exit strategies, bullish/bearish checklists
├── scripts/
│   ├── setup.py                   ← First-time setup (keypair generation, dependency install)
│   ├── cron-examples.sh           ← Example cron configurations for different monitoring strategies
│   ├── portfolio.sh               ← Check wallet balance, holdings, and PnL
│   ├── trending.sh                ← Scan trending tokens by volume
│   ├── analysis.sh                ← Full analysis dashboard (portfolio + signals + trending + candidates)
│   ├── swap.py                    ← Build, sign locally, and submit swap transactions
│   ├── test-api.sh                ← API connectivity test
│   └── trading-preferences.example.json  ← Trading preferences template
└── examples/
    ├── trading-workflow.py        ← Complete Python reference implementation
    └── deep-analysis-workflow.py  ← Holding trend analysis (cluster/smart money % of supply over time)

Agent creates these memory files at runtime:
  memory/
  ├── trading-journal.json         ← Every trade with entry reasoning + outcome
  ├── trading-lessons.md           ← Patterns learned from losses
  ├── trading-preferences.json     ← User-approved strategy parameters
  ├── trading-state.json           ← Runtime state (open positions, last scan)
  └── strategy-reviews/
      └── YYYY-MM-DD.md            ← Periodic aggregate performance reviews
```
