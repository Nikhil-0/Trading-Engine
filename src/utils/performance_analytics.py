import pandas as pd
import numpy as np
from typing import Dict, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class PerformanceAnalytics:
    @staticmethod
    def calculate_metrics(returns: pd.Series) -> Dict[str, float]:
        annual_factor = 252  # Trading days in a year
        
        # Basic metrics
        total_return = (1 + returns).prod() - 1
        annual_return = (1 + returns).prod() ** (annual_factor/len(returns)) - 1
        volatility = returns.std() * np.sqrt(annual_factor)
        
        # Risk metrics
        sharpe_ratio = np.sqrt(annual_factor) * returns.mean() / returns.std() if returns.std() != 0 else 0
        sortino_ratio = np.sqrt(annual_factor) * returns.mean() / returns[returns < 0].std() if len(returns[returns < 0]) > 0 else 0
        max_drawdown = ((1 + returns).cumprod() / (1 + returns).cumprod().cummax() - 1).min()
        
        # Additional metrics
        win_rate = len(returns[returns > 0]) / len(returns)
        avg_win = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0
        avg_loss = returns[returns < 0].mean() if len(returns[returns < 0]) > 0 else 0
        profit_factor = abs(returns[returns > 0].sum() / returns[returns < 0].sum()) if len(returns[returns < 0]) > 0 else float('inf')
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor
        }
    
    @staticmethod
    def plot_performance(equity_curve: pd.Series, trades: pd.DataFrame) -> None:
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Equity Curve', 'Drawdown', 'Trade PnL'),
            vertical_spacing=0.1,
            row_heights=[0.5, 0.25, 0.25]
        )

        # Equity curve
        fig.add_trace(
            go.Scatter(
                x=equity_curve.index,
                y=equity_curve.values,
                name='Portfolio Value',
                line=dict(color='blue')
            ),
            row=1, col=1
        )

        # Drawdown
        drawdown = (equity_curve / equity_curve.cummax() - 1) * 100
        fig.add_trace(
            go.Scatter(
                x=drawdown.index,
                y=drawdown.values,
                name='Drawdown %',
                line=dict(color='red')
            ),
            row=2, col=1
        )

        # Trade PnL
        fig.add_trace(
            go.Bar(
                x=trades.index,
                y=trades['pnl'],
                name='Trade PnL',
                marker_color=trades['pnl'].apply(lambda x: 'green' if x > 0 else 'red')
            ),
            row=3, col=1
        )

        fig.update_layout(
            height=1000,
            title='Trading Performance Analysis',
            showlegend=True
        )

        fig.show()