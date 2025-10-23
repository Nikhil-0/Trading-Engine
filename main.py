from src.data.data_fetcher import DataFetcher
from src.strategies.strategy import MovingAverageCrossover
from src.risk_management.risk_manager import RiskManager
from src.backtesting.backtester import Backtester

def main():
    # Initialize components
    strategy = MovingAverageCrossover(short_window=20, long_window=50)
    risk_manager = RiskManager(
        max_position_size=0.1,  # 10% of portfolio
        stop_loss=0.02,         # 2% stop loss
        take_profit=0.05        # 5% take profit
    )
    backtester = Backtester(
        initial_capital=100000,  # $100,000 initial capital
        commission=0.001        # 0.1% commission
    )
    
    # Run backtest
    results = backtester.run(
        symbol="AAPL", # Test with Apple stock
        strategy=strategy,
        risk_manager=risk_manager,
        start_date="2023-01-01",
        end_date="2023-12-31",
        interval="1d"
    )
    
    # Print results
    print("\nBacktest Results:")
    print(f"Initial Capital: ${results['initial_capital']:,.2f}")
    print(f"Final Portfolio Value: ${results['final_portfolio_value']:,.2f}")
    print(f"Total Return: {results['total_return']*100:.2f}%")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Profitable Trades: {results['profitable_trades']}")
    print(f"Win Rate: {results['win_rate']*100:.2f}%")
    print(f"Total PnL: ${results['total_pnl']:,.2f}")

if __name__ == "__main__":
    main()