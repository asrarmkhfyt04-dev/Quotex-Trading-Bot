# tests/test_risk_management.py

import pytest
from bot.risk_management import RiskManager

@pytest.fixture
def risk_manager():
    """
    Creates a RiskManager instance with default 2% stake 
    and 4% profit threshold.
    """
    return RiskManager(stake_pct=0.02, profit_pct=0.04)

def test_compute_stop_loss_balance(risk_manager):
    """
    Ensures compute_stop_loss_balance returns the balance 
    minus the stake percentage.
    """
    account_balance = 1000.0
    result = risk_manager.compute_stop_loss_balance(account_balance)
    # With stake_pct=0.02 => account_balance * (1.0 - 0.02) = 980.0
    assert result == 980.0, f"Expected 980.0, got {result}"

def test_compute_take_profit_balance(risk_manager):
    """
    Ensures compute_take_profit_balance returns the balance 
    plus the profit percentage.
    """
    account_balance = 1000.0
    result = risk_manager.compute_take_profit_balance(account_balance)
    # With profit_pct=0.04 => account_balance * (1.0 + 0.04) = 1040.0
    assert result == 1040.0, f"Expected 1040.0, got {result}"

def test_check_position_size(risk_manager):
    """
    Ensures check_position_size returns the correct stake 
    based on stake_pct of the account balance.
    """
    account_balance = 1000.0
    result = risk_manager.check_position_size(account_balance)
    # With stake_pct=0.02 => 2% of 1000 => 20.0
    assert result == 20.0, f"Expected 20.0, got {result}"
