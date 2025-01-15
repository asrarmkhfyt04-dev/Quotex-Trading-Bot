# config.py

# Import necessary libraries and packages
import os
from dotenv import load_dotenv

# Load environment variables 
load_dotenv()

# Load Quotex credentials
QUOTEX_USERNAME= os.environ.get('QUOTEX_USERNAME', 'demo@example.com')
QUOTEX_PASSWORD= os.environ.get('QUOTEX_PASSWORD', 'mypassword123')
USE_DEMO= os.environ.get("USE_DEMO", "false").lower() == "true"
print("DEBUG config.py => USE_DEMO =", USE_DEMO)

# Asset Name
ASSET_NAME = os.environ.get("ASSET_NAME", "AUD/USD (OTC)")

# Trading indicators
RSI_THRESHOLD= int(os.environ.get('RSI_THRESHOLD', 30))
MACD_FAST= int(os.environ.get('MACD_FAST', 12))
MACD_SLOW= int(os.environ.get('MACD_SLOW', 26))
MACD_SIGNAL= int(os.environ.get('MACD_SIGNAL', 9))

# Risk and trade settings
TRADE_AMOUNT= float(os.environ.get('TRADE_AMOUNT', 1.0))
BOLLINGER_PERIOD= int(os.environ.get('BOLLINGER_PERIOD', 20))
BOLLINGER_STD_DEV= float(os.environ.get('BOLLINGER_STD_DEV', 2.0))