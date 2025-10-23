from typing import Dict, Any
import pandas as pd
from datetime import datetime

class Executor:
    def __init__(self, commission: float = 0.001):  # 0.1% commission per trade
        self.commission = commission
        self.positions = {}  # Current positions
        self.trades = []     # Trade history
    
    def execute_trade(self,
                     symbol: str,
                     signal: int,
                     price: float,
                     size: float,
                     timestamp: datetime) -> Dict[str, Any]:

        trade = {
            'timestamp': timestamp,
            'symbol': symbol,
            'action': 'buy' if signal > 0 else 'sell',
            'price': price,
            'size': size,
            'commission': price * size * self.commission
        }
        
        # Update positions
        if symbol in self.positions:
            if signal != self.positions[symbol]['signal']:  # Close existing position
                trade['pnl'] = self._calculate_pnl(
                    symbol, 
                    self.positions[symbol]['price'],
                    price,
                    self.positions[symbol]['size'],
                    self.positions[symbol]['signal']
                )
                del self.positions[symbol]
            else:  # Add to existing position
                trade['pnl'] = 0
                self.positions[symbol]['size'] += size
                self.positions[symbol]['price'] = price  # Update average price
        else:  # New position
            trade['pnl'] = 0
            self.positions[symbol] = {
                'signal': signal,
                'price': price,
                'size': size
            }
        
        self.trades.append(trade)
        return trade
    
    def _calculate_pnl(self,
                      symbol: str,
                      entry_price: float,
                      exit_price: float,
                      size: float,
                      signal: int) -> float:

        gross_pnl = (exit_price - entry_price) * size * signal
        commission = (entry_price + exit_price) * size * self.commission
        return gross_pnl - commission
    
    def get_trade_history(self) -> pd.DataFrame:
        return pd.DataFrame(self.trades)