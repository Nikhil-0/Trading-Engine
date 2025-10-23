from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any

class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        pass

class MovingAverageCrossover(Strategy):
    def __init__(self, short_window: int = 20, long_window: int = 50):
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(index=data.index, data=0)
        
        # Generate signals
        signals[data['SMA_20'] > data['SMA_50']] = 1  # Buy signal
        signals[data['SMA_20'] < data['SMA_50']] = -1  # Sell signal
        
        return signals