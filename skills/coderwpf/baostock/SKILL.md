---
name: baostock
description: Free Chinese A-share stock data via BaoStock — K-lines, financials, industry classification, no registration required.
version: 1.0.0
homepage: https://www.baostock.com
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":["python3"]}}}
---

# BaoStock (证券宝 — 免费A股数据平台)

[BaoStock](https://www.baostock.com) is a free, open-source securities data platform for Chinese A-shares. No registration or API key needed. Returns `pandas.DataFrame`.

## Install

```bash
pip install baostock --upgrade
```

Verify:

```bash
python3 -c "import baostock as bs; lg = bs.login(); print(lg.error_msg); bs.logout()"
```

Should print `login success!`.

## Usage pattern

Every session must call `bs.login()` before queries and `bs.logout()` when done:

```python
import baostock as bs
import pandas as pd

lg = bs.login()

# ... queries here ...

bs.logout()
```

Result sets use `.get_data()` to get a DataFrame:

```python
rs = bs.query_all_stock()
df = rs.get_data()
```

## Core APIs

### 1. query_all_stock — List all securities

Get all stock/index codes for a given trading date.

```python
rs = bs.query_all_stock(day="2024-01-02")
df = rs.get_data()
# columns: code, tradeStatus, code_name
```

- **day** — Date string `YYYY-MM-DD` (default: today). Non-trading days return empty DataFrame.

### 2. query_history_k_data_plus — K-line data

Get historical K-line data (OHLCV + indicators).

```python
rs = bs.query_history_k_data_plus(
    "sh.601398",
    "date,code,open,high,low,close,volume,amount,pctChg",
    start_date="2024-01-01",
    end_date="2024-06-30",
    frequency="d",
    adjustflag="3"
)
df = rs.get_data()
```

**Parameters:**

- **code** — Stock code, format `sh.600000` or `sz.000001`
- **fields** — Comma-separated field names (see below)
- **start_date** / **end_date** — `YYYY-MM-DD`
- **frequency** — `d` (daily), `w` (weekly), `m` (monthly), `5`/`15`/`30`/`60` (minute bars). Index has no minute data.
- **adjustflag** — `1` (forward adj), `2` (backward adj), `3` (no adj, default)

**Available fields (daily):**

`date`, `code`, `open`, `high`, `low`, `close`, `preclose`, `volume`, `amount`, `adjustflag`, `turn` (turnover rate), `tradestatus`, `pctChg` (change %), `peTTM`, `pbMRQ`, `psTTM`, `pcfNcfTTM`, `isST`

**Minute bar fields:**

`date`, `time`, `code`, `open`, `high`, `low`, `close`, `volume`, `amount`, `adjustflag`

### 3. query_trade_dates — Trading calendar

```python
rs = bs.query_trade_dates(start_date="2024-01-01", end_date="2024-12-31")
df = rs.get_data()
# columns: calendar_date, is_trading_day
```

### 4. query_stock_industry — Industry classification

```python
rs = bs.query_stock_industry()
df = rs.get_data()
# columns: updateDate, code, code_name, industry, industryClassification
```

### 5. query_stock_basic — Stock basic info

```python
rs = bs.query_stock_basic(code="sh.601398")
df = rs.get_data()
# columns: code, code_name, ipoDate, outDate, type, status
```

- **type** — `1` stock, `2` index, `3` other
- **status** — `1` listed, `0` delisted

### 6. query_dividend_data — Dividend info

```python
rs = bs.query_dividend_data(code="sh.601398", year="2023", yearType="report")
df = rs.get_data()
```

- **yearType** — `report` (报告期) or `operate` (实施期)

### 7. Financial data (quarterly)

#### Profitability

```python
rs = bs.query_profit_data(code="sh.601398", year=2023, quarter=4)
df = rs.get_data()
# ROE, net profit margin, gross margin, etc.
```

#### Operating capacity

```python
rs = bs.query_operation_data(code="sh.601398", year=2023, quarter=4)
df = rs.get_data()
# Inventory turnover, AR turnover, etc.
```

#### Growth indicators

```python
rs = bs.query_growth_data(code="sh.601398", year=2023, quarter=4)
df = rs.get_data()
# YoY revenue growth, net profit growth, etc.
```

#### Balance sheet

```python
rs = bs.query_balance_data(code="sh.601398", year=2023, quarter=4)
df = rs.get_data()
# Current ratio, quick ratio, etc.
```

#### Cash flow

```python
rs = bs.query_cash_flow_data(code="sh.601398", year=2023, quarter=4)
df = rs.get_data()
```

#### Dupont analysis

```python
rs = bs.query_dupont_data(code="sh.601398", year=2023, quarter=4)
df = rs.get_data()
# ROE decomposition: profit margin × asset turnover × equity multiplier
```

### 8. Index data

#### Index constituents

```python
# 沪深300 constituents
rs = bs.query_hs300_stocks()
df = rs.get_data()

# 上证50
rs = bs.query_sz50_stocks()
df = rs.get_data()

# 中证500
rs = bs.query_zz500_stocks()
df = rs.get_data()
```

## Complete example: Download daily K-line to CSV

```python
import baostock as bs
import pandas as pd

bs.login()

rs = bs.query_history_k_data_plus(
    "sh.600519",
    "date,code,open,high,low,close,volume,amount,pctChg,peTTM",
    start_date="2024-01-01",
    end_date="2024-12-31",
    frequency="d",
    adjustflag="2"
)
df = rs.get_data()
df.to_csv("kweichow_moutai_2024.csv", index=False)
print(df.head())

bs.logout()
```

## Stock code format

- Shanghai: `sh.600000`, `sh.601398`
- Shenzhen: `sz.000001`, `sz.300750`
- Beijing: `bj.430047`
- Index: `sh.000001` (上证指数), `sh.000300` (沪深300)

## Tips

- **No registration or API key needed** — just `bs.login()`.
- Session may timeout after inactivity — call `bs.login()` again.
- **Not thread-safe** — use `multiprocessing` for parallel downloads, not threading.
- Data coverage: A-shares from 1990 to present.
- Financial data available quarterly with ~2 month delay after reporting period.
- Docs: http://baostock.com/baostock/index.php/Python_API%E6%96%87%E6%A1%A3
