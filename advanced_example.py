from src.data.data_manager import DataManager
from src.strategies.advanced_strategy import MLStrategy, EnsembleStrategy
from src.risk_management.advanced_risk import RiskManager, PortfolioOptimizer
from src.execution.advanced_executor import ExecutionHandler, OrderType, OrderSide
from src.utils.performance_analytics import PerformanceAnalytics
from src.utils.config import Config
import pandas as pd
from datetime import datetime, timedelta

def main():
    # Initialize components
    config = Config()
    data_manager = DataManager()
    execution_handler = ExecutionHandler()
    risk_manager = RiskManager()
    portfolio_optimizer = PortfolioOptimizer()
    performance_analytics = PerformanceAnalytics()
    
    # Set up ML strategy
    features = ['SMA_20', 'SMA_50', 'RSI', 'MACD', 'BB_Upper', 'BB_Lower', 'ATR']
    ml_strategy = MLStrategy(features=features)
    
    # Define symbols and timeframe
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Fetch data and prepare portfolio
    portfolio_data = {}
    portfolio_returns = pd.DataFrame()
    
    for symbol in symbols:
        # Fetch and prepare data
        data = data_manager.fetch_data(
            symbol=symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            interval='1d'
        )
        portfolio_data[symbol] = data
        portfolio_returns[symbol] = data['Close'].pct_change()
        
        # Train ML strategy
        ml_strategy.train(data)
    
    # Optimize portfolio weights
    optimization_result = portfolio_optimizer.optimize_portfolio(
        portfolio_returns,
        method='sharpe'
    )
    
    print("\nOptimal Portfolio Weights:")
    for symbol, weight in zip(symbols, optimization_result['weights']):
        print(f"{symbol}: {weight:.4f}")
    
    # Simulate trading
    portfolio_value = config.get('backtesting.initial_capital', 100000)
    current_prices = {symbol: data['Close'].iloc[-1] for symbol, data in portfolio_data.items()}
    
    for symbol, weight in zip(symbols, optimization_result['weights']):
        data = portfolio_data[symbol]
        signals = ml_strategy.generate_signals(data)
        
        if signals.iloc[-1] != 0:  # If we have a trading signal
            allocation = portfolio_value * weight
            price = current_prices[symbol]
            
            # Calculate position size using risk management
            volatility = data['Close'].pct_change().std()
            size = risk_manager.calculate_position_size(allocation, price, volatility)
            
            # Create order
            order = execution_handler.create_order(
                symbol=symbol,
                order_type=OrderType.MARKET,
                side=OrderSide.BUY if signals.iloc[-1] > 0 else OrderSide.SELL,
                quantity=size,
                price=price
            )
            
            print(f"\nCreated order for {symbol}:")
            print(f"Type: {order.order_type.value}")
            print(f"Side: {order.side.value}")
            print(f"Quantity: {order.quantity:.2f}")
            print(f"Price: ${order.price:.2f}")
    
    # Calculate portfolio metrics
    metrics = performance_analytics.calculate_metrics(portfolio_returns.mean(axis=1))
    
    print("\nPortfolio Performance Metrics:")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
    print(f"Sortino Ratio: {metrics['sortino_ratio']:.4f}")
    print(f"Max Drawdown: {metrics['max_drawdown']:.4%}")
    print(f"Annual Return: {metrics['annual_return']:.4%}")
    print(f"Win Rate: {metrics['win_rate']:.4%}")

if __name__ == "__main__":
    main()