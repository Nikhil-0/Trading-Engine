# Advanced Trading Engine

This is a sophisticated Python-based trading engine for quantitative finance, featuring machine learning strategies, advanced risk management, and comprehensive backtesting capabilities.

## Architecture Overview

The trading engine consists of four main components working together to provide a complete trading solution:

### 1. Data Management (`src/data/`)
- **Multi-source Data Fetching**
  - Yahoo Finance integration for stocks
  - Cryptocurrency exchange support via CCXT
  - Extensible data source interface
- **Technical Indicators**
  - Moving Averages (SMA 20, 50)
  - RSI (Relative Strength Index)
  - Bollinger Bands
  - MACD (Moving Average Convergence Divergence)
  - ATR (Average True Range)
  - OBV (On Balance Volume)
- **Data Validation and Preprocessing**
  - Automated data cleaning
  - Missing value handling
  - Date alignment

### 2. Strategy Implementation (`src/strategies/`)
- **Machine Learning Strategy**
  - Feature engineering from technical indicators
  - Model training and prediction
  - Signal generation with confidence thresholds
- **Ensemble Strategy**
  - Multiple strategy combination
  - Weighted signal aggregation
- **Strategy Optimization**
  - Parameter optimization using Optuna
  - Performance metric selection
  - Cross-validation support

### 3. Risk Management (`src/risk_management/`)
- **Portfolio Optimization**
  - Sharpe ratio maximization
  - Variance minimization
  - Diversification optimization
- **Position Sizing**
  - Volatility-adjusted sizing
  - Risk-based allocation
  - Correlation consideration
- **Risk Monitoring**
  - Stop-loss and take-profit management
  - Portfolio risk metrics
  - Drawdown monitoring

### 4. Trade Execution (`src/execution/`)
- **Order Management**
  - Multiple order types (market, limit, stop)
  - Position tracking
  - Trade history maintenance
- **Transaction Cost Analysis**
  - Commission handling
  - Slippage modeling
- **Performance Analytics**
  - Real-time P&L tracking
  - Performance metrics calculation
  - Trade statistics

## Project Structure

```
Trading Engine/
├── src/
│   ├── data/                  # Data management
│   │   ├── data_manager.py    # Main data handling
│   │   └── __init__.py
│   ├── strategies/            # Trading strategies
│   │   ├── advanced_strategy.py   # ML and ensemble strategies
│   │   └── __init__.py
│   ├── risk_management/       # Risk management
│   │   ├── advanced_risk.py   # Portfolio and risk management
│   │   └── __init__.py
│   ├── execution/             # Trade execution
│   │   ├── advanced_executor.py    # Order execution
│   │   └── __init__.py
│   └── utils/                 # Utilities
│       ├── config.py          # Configuration management
│       ├── logger.py          # Logging setup
│       └── performance_analytics.py  # Performance metrics
├── tests/                     # Unit tests
├── requirements.txt           # Project dependencies
├── main.py                   # Basic example
├── advanced_example.py        # Advanced ML strategy example
└── README.md                 # Documentation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Nikhil-0/trading-engine.git
cd trading-engine
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Basic Usage

Here's a simple example of using the trading engine with a machine learning strategy:

```python
from src.data.data_manager import DataManager
from src.strategies.advanced_strategy import MLStrategy
from src.risk_management.advanced_risk import PortfolioOptimizer
from src.execution.advanced_executor import OrderExecutor

# Initialize components
data_manager = DataManager()
strategy = MLStrategy()
risk_manager = PortfolioOptimizer()
executor = OrderExecutor()

# Fetch and process data
symbols = ['AAPL', 'MSFT', 'GOOGL']
data = data_manager.fetch_data(symbols, start='2023-01-01')
features = data_manager.calculate_indicators(data)

# Train strategy and generate signals
strategy.train(features, target='returns')
signals = strategy.generate_signals(features)

# Optimize portfolio
weights = risk_manager.optimize_portfolio(data, signals)

# Execute trades
for symbol, weight in zip(symbols, weights):
    executor.place_order(symbol, weight)
```

## Advanced Features

### Custom Strategy Development

You can create custom strategies by inheriting from the base Strategy class:

```python
from src.strategies.advanced_strategy import BaseStrategy
import numpy as np

class CustomStrategy(BaseStrategy):
    def generate_signals(self, data):
        signals = {}
        for symbol in data.columns.levels[0]:
            # Custom signal logic
            sma_20 = data[symbol]['SMA_20']
            sma_50 = data[symbol]['SMA_50']
            signals[symbol] = np.where(sma_20 > sma_50, 1, -1)
        return signals
```

### Risk Management Configuration

Configure risk parameters for portfolio optimization:

```python
risk_manager = PortfolioOptimizer(
    target_return=0.15,        # 15% target annual return
    max_volatility=0.20,       # 20% maximum volatility
    risk_free_rate=0.03,       # 3% risk-free rate
    max_position_size=0.25     # 25% maximum position size
)
```

### Performance Analytics

Monitor and analyze trading performance:

```python
from src.utils.performance_analytics import PerformanceAnalytics

analytics = PerformanceAnalytics()
metrics = analytics.calculate_metrics(returns)
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")
print(f"Annual Return: {metrics['annual_return']:.2%}")
```

## Development Tools

### Testing
- Comprehensive test suite using pytest
- Unit tests for each component
- Integration tests for the complete system
- Test coverage reporting
- See `tests/README.md` for detailed testing guide

### Docker Support
- Dockerfile for containerized deployment
- docker-compose.yml for easy development setup
- Multi-stage build for optimized images
- Volume mounting for data persistence

### Error Handling
- Robust error handling system
- Retry mechanism with exponential backoff
- Custom exception hierarchy
- Detailed error logging

### CI/CD Pipeline
- GitHub Actions workflow
- Automated testing on multiple Python versions
- Docker image building and pushing
- Code coverage reporting

### Logging
- Structured logging configuration
- Log rotation
- Separate info and error log files
- Console and file handlers

## Deployment

### Using Docker

1. Build the image:
```bash
docker build -t trading-engine .
```

2. Run with Docker Compose:
```bash
docker-compose up -d
```

### Manual Deployment

1. Set up logging:
```bash
mkdir -p logs
python -c "import logging; logging.basicConfig(filename='logs/trading_engine.log')"
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Run the engine:
```bash
py main.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details
```

## Features

- Data fetching from Yahoo Finance
- Technical indicator calculation
- Strategy implementation framework
- Risk management system
- Trade execution simulation
- Comprehensive backtesting

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the sample backtest:

```python
py main.py
```

The sample code demonstrates a Moving Average Crossover strategy on Apple (AAPL) stock.

## Extending the Engine

### Adding New Strategies

Create a new strategy by inheriting from the `Strategy` base class:

```python
from src.strategies.strategy import Strategy

class MyStrategy(Strategy):
    def generate_signals(self, data):
        # Implement your strategy logic here
        pass
```

### Customizing Risk Management

Modify risk parameters in `RiskManager`:

```python
risk_manager = RiskManager(
    max_position_size=0.1,  # 10% of portfolio
    stop_loss=0.02,         # 2% stop loss
    take_profit=0.05        # 5% take profit
)
```

## Contributing

Feel free to submit issues and enhancement requests.
