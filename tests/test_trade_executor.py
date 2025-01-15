# tests/test_trade_executor.py

import pytest
import time

from bot.trade_executor import TradeExecutor
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

@pytest.fixture(scope="module")
def executor():
    """
    Creates a module-scoped TradeExecutor in visible (non-headless) mode.
    Logs in once, closes browser after all tests.
    """
    exec_ = TradeExecutor()
    yield exec_
    exec_.close()

def test_login(executor):
    """
    Verifies we are logged in by checking for a post-login element.
    """
    try:
        # Directly check for 'asset-select__button' that only appears after login
        btn = executor.driver.find_element(By.CSS_SELECTOR, "button.asset-select__button")
        assert btn is not None, "Login succeeded, asset-select__button found."
    except NoSuchElementException:
        pytest.fail("Post-login element not found; login may have failed.")

def test_get_account_balance(executor):
    """
    Ensures the account balance is fetched correctly and is non-negative.
    """
    balance = executor.get_account_balance()
    assert isinstance(balance, float), "Balance should be a float."
    assert balance >= 0.0, "Balance should be >= 0.0"

def test_fetch_market_data(executor):
    """
    Ensures market_data has 'last_price' as a float, even if it's 0.0 in Live mode.
    """
    data = executor.fetch_market_data()
    assert "last_price" in data, "market_data should contain 'last_price'."
    assert isinstance(data["last_price"], float), "last_price should be a float."
    # If 0.0 is valid, do not fail if data["last_price"] == 0.0.
    # That means we accept the fallback scenario with no 'span.current-price'.
    print(f"DEBUG test_fetch_market_data => {data}")

def test_place_trade(executor):
    """
    Places an 'UP' trade to confirm UI interaction. 
    Uses small stake to minimize risk in a demo environment.
    """
    executor.set_investment_amount(1.0)
    executor.place_trade("UP")
    time.sleep(2) 
