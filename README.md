# Quotex Trading Bot

A fully automated Python bot to trade on the [Quotex](https://qxbroker.com) platform via browser automation.  
It supports **Demo** or **Live** mode, **automated technical analysis** (RSI, MACD, Bollinger Bands), and **configurable risk management** (stake percentage, profit threshold).

---

## 1. Features

1. **Automated Browser Control**  
   - Uses **Selenium**-like automation (via [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver))  
   - **Logs in** with your Quotex credentials, toggles Demo vs. Live, selects an asset if desired, and places trades.

2. **Technical Analysis**  
   - **RSI** (Relative Strength Index)  
   - **MACD** (Moving Average Convergence Divergence)  
   - **Bollinger Bands**  
   - All customizable (periods, thresholds) through environment variables or config.

3. **Risk Management**  
   - Trades a fixed fraction (e.g., 2%) of your account balance.  
   - (Optional) 2%/4% logic for stop-loss or profit targeting (adapted to binary options context).

4. **Modular & Extensible**  
   - Separate files: `strategy.py` for signals, `trade_executor.py` for Selenium, `risk_management.py` for stake sizing, etc.
   - Easy to tweak or replace indicators.

5. **Configurable**  
   - `.env` file to store credentials (`QUOTEX_USERNAME`, `QUOTEX_PASSWORD`), toggling demo (`USE_DEMO`), asset selection, etc.
   - Minimal updates needed for each environment.

---

## 2. Project Structure

Quotex-Trading-Bot/
├── bot/
│   ├── __init__.py
│   ├── config.py
│   ├── indicators.py
│   ├── risk_management.py
│   ├── strategy.py
│   ├── trade_executor.py
│   └── main.py
├── tests/
│   ├── test_strategy_logic.py
│   ├── test_trade_executor.py
│   ├── test_end_to_end.py
│   └── test_risk_management.py
├── requirements.txt
├── .env.example
├── README.md
└── LICENSE


**Key Files**:

1. **`bot/config.py`**  
   - Loads environment variables from `.env`  
   - Provides global constants like `QUOTEX_USERNAME`, `QUOTEX_PASSWORD`, `USE_DEMO`, `ASSET_NAME`, etc.

2. **`bot/indicators.py`**  
   - Implements `calculate_rsi()`, `calculate_macd()`, `calculate_bollinger_bands()` via `pandas_ta`.

3. **`bot/risk_management.py`**  
   - Defines `RiskManager` with a stake percentage (e.g., 2%) of account balance.  
   - Optionally includes logic for stop-loss / take-profit thresholds if needed.

4. **`bot/strategy.py`**  
   - Defines `TradingStrategy`, combining RSI + MACD + Bollinger signals into final `BUY`, `SELL`, or `HOLD`.

5. **`bot/trade_executor.py`**  
   - Selenium-based automation (using `undetected_chromedriver`).
   - Logs in, toggles Demo/Live, sets trade amount, selects an asset, places trades, etc.

6. **`bot/main.py`**  
   - The main orchestrator:
     1. Initializes `TradeExecutor`, `TradingStrategy`, `RiskManager`.
     2. Fetches data in a loop, calls signals, places trades, sleeps, etc.
   - **Run this** (`python bot/main.py`) for a continuous trading loop.

7. **`tests/*`**  
   - **`test_trade_executor.py`** checks login, fetching balance, placing a test trade.  
   - **`test_strategy_logic.py`** mocks RSI/MACD/Boll calls and verifies `BUY/SELL/HOLD` logic.  
   - **`test_end_to_end.py`** does a full integration (login, fetch data, create signals, place trades).
   - **`test_risk_management.py`** checks risk sizing, etc.

---

## 3. Installation

### 3.1. Prerequisites
- **Python 3.9+** recommended (3.7+ might work, but 3.9+ is ideal).
- **Chrome Browser** installed (latest stable).
- **ChromeDriver** is auto-managed by `undetected_chromedriver`, no separate install needed.

### 3.2. Steps

1. **Clone or Download** this repository:
   ```bash
   git clone https://github.com/carlosrod723/Quotex-Trading-Bot.git
   cd Quotex-Trading-Bot
   ```

2. Create and Activate a Virtual Environment (optional but recommended):
    ```
    python -m venv venv
    source venv/bin/activate  # on Linux/macOS
    # or venv\Scripts\activate on Windows
    ```

3. Install Dependencies:

    ```
    pip install -r requirements.txt
    ```

4. Set Up .env:
    Copy .env.example to .env:
    ```
    cp .env.example .env
    ```

    Edit .env with your credentials:
    ```
    QUOTEX_USERNAME=your_email_here
    QUOTEX_PASSWORD=your_password_here
    USE_DEMO=true 
    ASSET_NAME="EUR/USD (OTC)" 

Note-
* If USE_DEMO=true, it will use Demo Account. If USE_DEMO=false, it will use Live Account
* You may change the ASSET_NAME to asset of your choice

## 4. Usage

### 4.1. Basic Execution

Simply run:
    ```
    python bot/main.py
    ```
What happens:

Chrome browser opens automatically.
Logs in to Quotex with your credentials from .env.
If USE_DEMO=true, toggles to Demo; if false, stays in Live mode.
Repeatedly:
Fetches your account balance and market data.
Applies the strategy (RSI, MACD, Bollinger).
Places a trade if strategy says BUY or SELL.
Sleeps 5 minutes, then repeats.
Press Ctrl + C in the terminal to stop the bot gracefully.

### 4.2. Changing Indicators or Thresholds
Adjust RSI thresholds, MACD periods, or Bollinger parameters in .env or directly in config.py.
If you want a different technical logic, modify bot/strategy.py.

### 4.3. Risk & Stake Percentage
By default, RiskManager uses stake_pct=0.02 (2%).
Change it in .env or in main.py if you prefer a different fraction.

### 4.4. Demo vs. Live
The bot automatically uses Demo if USE_DEMO=true.
If you want Live trades, set it to false in .env.

## 5. Testing
tests/test_trade_executor.py
Verifies login, fetching account balance, placing a small trade (skipped by default).
tests/test_strategy_logic.py
Mocks RSI/MACD/Boll and checks if final signal matches expected (BUY/SELL/HOLD).
tests/test_end_to_end.py
Runs a real end-to-end flow: login, gather data, generate signal, place a trade in Demo.
tests/test_risk_management.py
Checks the position-sizing logic.

Run them:
```
python -m pytest -v
```

## 6. FAQ
Q: Does this guarantee profit?
A: No, it’s simply an automated strategy. Market risk remains.

Q: Can I change the frequency?
A: Yes. In main.py, change time.sleep(5 * 60) to your desired interval.

Q: What if Quotex’s UI changes?
A: Selenium selectors might break. You’d need to update the CSS selectors or XPaths in trade_executor.py.

Q: How can I see the logs?
A: The console output from main.py includes logs. You can also integrate Python’s logging to file.

## 7. License & Disclaimer
This project is licensed under the MIT License (see LICENSE file).
Note: Automated trading involves risk; use at your own discretion and responsibility.

Enjoy trading on Quotex, and good luck!