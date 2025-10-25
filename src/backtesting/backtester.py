import pandas as pd
import numpy as np
from typing import Dict, Any
from ..data.data_fetcher import DataFetcher
from ..strategies.strategy import Strategy
from ..risk_management.risk_manager import RiskManager
from ..execution.executor import Executor

class Backtester:
    def __init__(self,
                 initial_capital: float = 100000.0,
                 commission: float = 0.001):
        self.initial_capital = initial_capital
        self.data_fetcher = DataFetcher()
        self.executor = Executor(commission=commission)
        
    def run(self,
            symbol: str,
            strategy: Strategy,
            risk_manager: RiskManager,
            start_date: str,
            end_date: str,
            interval: str = "1d") -> Dict[str, Any]:

        # Fetch historical data
        data = self.data_fetcher.fetch_data(
            symbol,
            start_date,
            end_date,
            interval
        )
        
        # Generate trading signals
        signals = strategy.generate_signals(data)
        
        # Initialize tracking variables
        portfolio_value = self.initial_capital
        position = 0
        entry_price = 0
        
        for timestamp, signal in signals.items():
            current_price = data.loc[timestamp, 'Close']
            
            # Calculate volatility for position sizing
            volatility = data['Close'].rolling(window=20).std().loc[timestamp]
            
            if position == 0 and signal != 0:  # New position
                size = risk_manager.calculate_position_size(
                    portfolio_value,
                    current_price,
                    volatility
                )
                trade = self.executor.execute_trade(
                    symbol,
                    signal,
                    current_price,
                    size,
                    timestamp
                )
                position = signal
                entry_price = current_price
                portfolio_value -= trade['commission']
                
            elif position != 0:  # Existing position
                # Check stop loss and take profit
                if (risk_manager.check_stop_loss(entry_price, current_price, position) or
                    risk_manager.check_take_profit(entry_price, current_price, position) or
                    signal == -position):  # Exit signal
                    
                    size = self.executor.positions[symbol]['size']
                    trade = self.executor.execute_trade(
                        symbol,
                        -position,
                        current_price,
                        size,
                        timestamp
                    )
                    portfolio_value += trade['pnl']
                    position = 0
                    entry_price = 0
        
        # Calculate performance metrics

        trade_history = self.executor.get_trade_history()
        total_trades = len(trade_history)
        if 'pnl' in trade_history.columns:
            profitable_trades = len(trade_history[trade_history['pnl'] > 0])
            total_pnl = trade_history['pnl'].sum()
        else:
            print("Column 'pnl' not found in trade_history. Check data pipeline.")
            profitable_trades = 0
            total_pnl = 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_portfolio_value': portfolio_value,
            'total_return': (portfolio_value - self.initial_capital) / self.initial_capital,
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': profitable_trades / total_trades if total_trades > 0 else 0,
            'total_pnl': total_pnl,
            'trade_history': trade_history
        }