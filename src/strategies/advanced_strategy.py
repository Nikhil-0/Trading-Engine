from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import optuna
from ..utils.logger import setup_logger
from ..utils.config import Config

logger = setup_logger(__name__)
config = Config()

class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        pass
    
    @abstractmethod
    def optimize(self, data: pd.DataFrame, objective: str = 'sharpe_ratio') -> Dict[str, Any]:
        pass

class MLStrategy(Strategy):
    def __init__(self,
                 features: List[str],
                 lookback: int = 20,
                 threshold: float = 0.5):
        self.features = features
        self.lookback = lookback
        self.threshold = threshold
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        feature_data = []
        for feature in self.features:
            if feature in data.columns:
                feature_data.append(data[feature])
            else:
                logger.warning(f"Feature {feature} not found in data")
        
        if not feature_data:
            return np.empty((0, len(self.features)))
        X = np.column_stack(feature_data)
        if X.shape[0] == 0:
            return X
        X = self.scaler.fit_transform(X)
        return X
    
    def _prepare_labels(self, data: pd.DataFrame) -> np.ndarray:
        # Calculate future returns
        future_returns = data['Close'].pct_change(self.lookback).shift(-self.lookback)
        # Create binary labels (1 for positive returns, 0 for negative)
        y = (future_returns > 0).astype(int)
        return y[:-self.lookback]  # Remove last lookback periods where we don't have labels
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        X = self._prepare_features(data)
        if X.shape[0] == 0 or not hasattr(self.model, "n_classes_"):
            print("Model not fitted or no data available for signal generation. Skipping.")
            return pd.Series(index=data.index, data=0)
        probas = self.model.predict_proba(X)
        signals = pd.Series(index=data.index, data=0)
        signals[probas[:, 1] > self.threshold] = 1
        signals[probas[:, 1] < (1 - self.threshold)] = -1
        return signals
    
    def train(self, data: pd.DataFrame) -> None:
        X = self._prepare_features(data[:-self.lookback])  # Remove last lookback periods
        y = self._prepare_labels(data)
        if X.shape[0] == 0 or y.shape[0] == 0:
            print("No data available for training. Skipping ML training.")
            return
        self.model.fit(X, y)
    
    def optimize(self, data: pd.DataFrame, objective: str = 'sharpe_ratio') -> Dict[str, Any]:
        def objective_function(trial):
            # Define parameter space
            self.threshold = trial.suggest_float('threshold', 0.5, 0.9)
            self.lookback = trial.suggest_int('lookback', 5, 50)
            
            # Train and generate signals
            self.train(data)
            signals = self.generate_signals(data)
            
            # Calculate returns
            returns = data['Close'].pct_change() * signals.shift(1)
            
            # Calculate objective metric
            if objective == 'sharpe_ratio':
                return returns.mean() / returns.std() * np.sqrt(252)
            elif objective == 'returns':
                return returns.sum()
            else:
                raise ValueError(f"Unknown objective: {objective}")
        
        # Create and run optimization study
        study = optuna.create_study(direction='maximize')
        study.optimize(objective_function, n_trials=100)
        
        # Update parameters with best values
        self.threshold = study.best_params['threshold']
        self.lookback = study.best_params['lookback']
        
        return {
            'best_params': study.best_params,
            'best_value': study.best_value
        }

class EnsembleStrategy(Strategy):
    def __init__(self, strategies: List[Strategy], weights: Optional[List[float]] = None):
        self.strategies = strategies
        self.weights = weights if weights is not None else [1/len(strategies)] * len(strategies)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        combined_signals = pd.Series(0, index=data.index)
        
        for strategy, weight in zip(self.strategies, self.weights):
            signals = strategy.generate_signals(data)
            combined_signals += signals * weight
        
        # Normalize signals
        combined_signals = combined_signals.apply(lambda x: 1 if x > 0.5 else (-1 if x < -0.5 else 0))
        return combined_signals
    
    def optimize(self, data: pd.DataFrame, objective: str = 'sharpe_ratio') -> Dict[str, Any]:
        def objective_function(trial):
            # Optimize weights
            weights = [trial.suggest_float(f'weight_{i}', 0, 1) for i in range(len(self.strategies))]
            weights = np.array(weights) / sum(weights)  # Normalize weights
            
            self.weights = weights
            signals = self.generate_signals(data)
            returns = data['Close'].pct_change() * signals.shift(1)
            
            if objective == 'sharpe_ratio':
                return returns.mean() / returns.std() * np.sqrt(252)
            elif objective == 'returns':
                return returns.sum()
            else:
                raise ValueError(f"Unknown objective: {objective}")
        
        study = optuna.create_study(direction='maximize')
        study.optimize(objective_function, n_trials=100)
        
        self.weights = [study.best_params[f'weight_{i}'] for i in range(len(self.strategies))]
        self.weights = np.array(self.weights) / sum(self.weights)
        
        return {
            'best_params': study.best_params,
            'best_value': study.best_value
        }