# risk_management.py

class RiskManager:
    """
    Manages risk logic based on the total account balance.

    By default:
      - stake_pct=0.02  => 2% of account used as stake each trade
      - profit_pct=0.04 => 4% of account used for a 'take-profit' style threshold
    """

    def __init__(self, stake_pct=0.02, profit_pct=0.04):
        """
        :param stake_pct: Fraction of the account used for each trade stake 
                          (e.g. 0.02 for 2%).
        :param profit_pct: Fraction of the account for a 'take-profit' threshold 
                           (e.g. 0.04 for 4%).
        """
        self.stake_pct  = stake_pct
        self.profit_pct = profit_pct

    def compute_stop_loss_balance(self, account_balance: float) -> float:
        """
        Returns the account-balance threshold below which the bot 
        might stop trading to limit drawdowns.
        
        Example: If stake_pct=0.02 and balance=10,000 => threshold=9,800
                 meaning if the account dips below $9,800, 
                 we may stop opening new trades.
        
        :param account_balance: Current total account balance
        :return: The 'stop-loss' balance threshold
        """
        return account_balance * (1.0 - self.stake_pct)

    def compute_take_profit_balance(self, account_balance: float) -> float:
        """
        Returns the account-balance threshold above which the bot 
        might stop trading to secure gains.
        
        Example: If profit_pct=0.04 and balance=10,000 => threshold=10,400 
                 meaning if we exceed $10,400, 
                 we may stop opening new trades.
        
        :param account_balance: Current total account balance
        :return: The 'take-profit' balance threshold
        """
        return account_balance * (1.0 + self.profit_pct)

    def check_position_size(self, account_balance: float) -> float:
        """
        Computes the actual stake size to open each trade, 
        as a fraction of the entire account balance.
        
        Example: If stake_pct=0.02 and balance=10,000 => trade_size=200
        
        :param account_balance: Current total account balance
        :return: Monetary amount to stake on a single trade
        """
        return account_balance * self.stake_pct
