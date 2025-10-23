from typing import Dict, Any
import pandas as pd

class RiskManager:
    def __init__(self, 
                 max_position_size: float = 0.1,  # Maximum position size as fraction of portfolio
                 stop_loss: float = 0.02,         # Stop loss as fraction of position
                 take_profit: float = 0.05):      # Take profit as fraction of position
        self.max_position_size = max_position_size
        self.stop_loss = stop_loss
        self.take_profit = take_profit
    
    def calculate_position_size(self, 
                              portfolio_value: float,
                              current_price: float,
                              volatility: float) -> float:

        max_position_value = portfolio_value * self.max_position_size
        risk_adjusted_size = max_position_value / (volatility * current_price)
        return min(risk_adjusted_size, max_position_value / current_price)
    
    def check_stop_loss(self, 
                       entry_price: float,
                       current_price: float,
                       position: int) -> bool:

        if position > 0:  # Long position
            return current_price < entry_price * (1 - self.stop_loss)
        elif position < 0:  # Short position
            return current_price > entry_price * (1 + self.stop_loss)
        return False
    
    def check_take_profit(self,
                         entry_price: float,
                         current_price: float,
                         position: int) -> bool:

        if position > 0:  # Long position
            return current_price > entry_price * (1 + self.take_profit)
        elif position < 0:  # Short position
            return current_price < entry_price * (1 - self.take_profit)
        return False