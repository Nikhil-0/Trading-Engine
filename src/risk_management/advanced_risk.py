import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from scipy.optimize import minimize
from ..utils.logger import setup_logger
from ..utils.config import Config

logger = setup_logger(__name__)
config = Config()

class PortfolioOptimizer:
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
    
    def optimize_portfolio(self,
                         returns: pd.DataFrame,
                         method: str = 'sharpe') -> Dict[str, Any]:

        if method == 'sharpe':
            return self._maximize_sharpe_ratio(returns)
        elif method == 'min_var':
            return self._minimize_variance(returns)
        elif method == 'max_div':
            return self._maximize_diversification(returns)
        else:
            raise ValueError(f"Unknown optimization method: {method}")
    
    def _maximize_sharpe_ratio(self, returns: pd.DataFrame) -> Dict[str, Any]:
        n_assets = len(returns.columns)
        
        def objective(weights):
            portfolio_return = np.sum(returns.mean() * weights) * 252
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return -sharpe_ratio  # Minimize negative Sharpe ratio
        
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
        ]
        bounds = tuple((0, 1) for _ in range(n_assets))  # Weights between 0 and 1
        
        result = minimize(
            objective,
            x0=np.array([1/n_assets] * n_assets),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return {
            'weights': result.x,
            'sharpe_ratio': -result.fun,
            'success': result.success
        }
    
    def _minimize_variance(self, returns: pd.DataFrame) -> Dict[str, Any]:
        n_assets = len(returns.columns)
        
        def objective(weights):
            return np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
        
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        ]
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        result = minimize(
            objective,
            x0=np.array([1/n_assets] * n_assets),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return {
            'weights': result.x,
            'volatility': result.fun,
            'success': result.success
        }
    
    def _maximize_diversification(self, returns: pd.DataFrame) -> Dict[str, Any]:
        n_assets = len(returns.columns)
        
        def objective(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
            weighted_vols = np.sum(np.sqrt(np.diag(returns.cov() * 252)) * weights)
            diversification_ratio = weighted_vols / portfolio_vol
            return -diversification_ratio
        
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        ]
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        result = minimize(
            objective,
            x0=np.array([1/n_assets] * n_assets),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return {
            'weights': result.x,
            'diversification_ratio': -result.fun,
            'success': result.success
        }

class RiskManager:
    def __init__(self,
                 max_position_size: float = 0.1,
                 stop_loss: float = 0.02,
                 take_profit: float = 0.05,
                 max_drawdown: float = 0.25,
                 var_confidence: float = 0.95):
        self.max_position_size = max_position_size
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.max_drawdown = max_drawdown
        self.var_confidence = var_confidence
        self.portfolio_optimizer = PortfolioOptimizer()
    
    def calculate_position_size(self,
                              portfolio_value: float,
                              current_price: float,
                              volatility: float,
                              correlation: Optional[float] = None) -> float:

        # Basic position size
        max_position_value = portfolio_value * self.max_position_size
        
        # Adjust for volatility
        vol_adjustment = 1 / (1 + volatility)
        
        # Adjust for correlation if provided
        if correlation is not None:
            correlation_adjustment = 1 - abs(correlation)
        else:
            correlation_adjustment = 1
        
        # Calculate final position size
        adjusted_position_value = max_position_value * vol_adjustment * correlation_adjustment
        return min(adjusted_position_value / current_price, max_position_value / current_price)
    
    def calculate_var(self,
                     returns: pd.Series,
                     position_value: float) -> float:

        return position_value * np.percentile(returns, (1 - self.var_confidence) * 100)
    
    def calculate_trailing_stop(self,
                              entry_price: float,
                              current_price: float,
                              high_price: float,
                              atr: float,
                              multiplier: float = 2.0) -> float:

        atr_stop = current_price - (atr * multiplier)
        initial_stop = entry_price * (1 - self.stop_loss)
        trailing_stop = high_price * (1 - self.stop_loss)
        
        return max(atr_stop, initial_stop, trailing_stop)
    
    def update_portfolio_risk(self,
                            positions: Dict[str, Dict],
                            returns: pd.DataFrame) -> Dict[str, Any]:

        # Calculate portfolio metrics
        portfolio_return = np.sum(returns.mean() * list(positions.values()))
        portfolio_vol = np.sqrt(np.dot(
            list(positions.values()),
            np.dot(returns.cov(), list(positions.values()))
        ))
        
        # Check if rebalancing is needed
        if portfolio_vol > self.max_drawdown:
            # Optimize portfolio
            optimization_result = self.portfolio_optimizer.optimize_portfolio(returns)
            
            return {
                'rebalance_needed': True,
                'optimal_weights': optimization_result['weights'],
                'current_risk': portfolio_vol,
                'sharpe_ratio': (portfolio_return - 0.02) / portfolio_vol
            }
        
        return {
            'rebalance_needed': False,
            'current_risk': portfolio_vol,
            'sharpe_ratio': (portfolio_return - 0.02) / portfolio_vol
        }