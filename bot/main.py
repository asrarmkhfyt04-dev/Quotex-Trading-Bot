# main.py

import time
import logging

# Import custom modules
from .strategy import TradingStrategy
from .risk_management import RiskManager
from .trade_executor import TradeExecutor

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def main():
    """
    Main orchestrator that continuously:
      1) Initializes the TradeExecutor, TradingStrategy, RiskManager
      2) Fetches account balance & market data
      3) Generates signals, applies risk mgmt, places trades
      4) Sleeps for 5 minutes, then repeats
    """

    logging.info("Initializing TradeExecutor...")
    # If you want to be truly headless on a server, set headless=True
    executor = TradeExecutor()  # by default uses non-headless in your code
    # OR: executor = TradeExecutor(headless=True) if you’ve added that param

    logging.info("Initializing TradingStrategy...")
    strategy = TradingStrategy()  # e.g. rsi_buy=25, rsi_sell=75 if you want the stricter version

    logging.info("Initializing RiskManager (2% stake, 4% profit threshold)...")
    risk_manager = RiskManager(stake_pct=0.02, profit_pct=0.04)

    try:
        while True:
            logging.info("===== New Cycle =====")

            # 1) Get account balance
            account_balance = executor.get_account_balance()
            logging.info(f"Account Balance: {account_balance:.2f}")

            # 2) Determine stake size (e.g., 2% of current balance)
            trade_amount = risk_manager.check_position_size(account_balance)
            logging.info(f"Trade Amount: {trade_amount:.2f}")

            # 3) Fetch or mock market data
            market_data = executor.fetch_market_data()
            logging.info(f"Fetched market data: {market_data}")

            # 4) Generate signal from the strategy
            signal = strategy.generate_signal(market_data)
            logging.info(f"Strategy Signal: {signal}")

            # 5) Place a trade if signal is BUY or SELL
            if signal == "BUY":
                executor.set_investment_amount(trade_amount)
                # Optionally set expiry time, e.g. executor.set_trade_time("00:01:00")
                executor.place_trade("UP")
                logging.info("Placed an UP (BUY) trade.")
            elif signal == "SELL":
                executor.set_investment_amount(trade_amount)
                # Optionally set expiry time, e.g. executor.set_trade_time("00:01:00")
                executor.place_trade("DOWN")
                logging.info("Placed a DOWN (SELL) trade.")
            else:
                logging.info("No trade this cycle (signal is HOLD or unrecognized).")

            # 6) Sleep 5 minutes (300 seconds)
            logging.info("Cycle complete. Sleeping 5 minutes...")
            time.sleep(5 * 60)

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received; shutting down gracefully.")

    finally:
        logging.info("Closing the Selenium driver...")
        executor.close()

if __name__ == "__main__":
    main()
