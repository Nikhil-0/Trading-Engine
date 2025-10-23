# Testing Guide

This guide explains how to run and write tests for the Trading Engine.

## Running Tests

To run all tests:
```bash
pytest tests/
```

To run specific test files:
```bash
pytest tests/test_data_manager.py
pytest tests/test_strategies.py
```

To run tests with coverage:
```bash
pytest --cov=src tests/
```

## Writing Tests

Each component should have its own test file:
- `test_data_manager.py` - Tests for data fetching and processing
- `test_strategies.py` - Tests for trading strategies
- `test_risk_manager.py` - Tests for risk management
- `test_executor.py` - Tests for trade execution

Example test structure:

```python
import pytest
from src.data.data_manager import DataManager

def test_data_fetching():
    data_manager = DataManager()
    data = data_manager.fetch_data(
        symbol="AAPL",
        start_date="2023-01-01",
        end_date="2023-12-31"
    )
    assert not data.empty
    assert "Close" in data.columns
    assert "SMA_20" in data.columns

def test_indicator_calculation():
    data_manager = DataManager()
    data = data_manager.fetch_data("AAPL", "2023-01-01", "2023-12-31")
    
    # Test RSI calculation
    assert "RSI" in data.columns
    assert data["RSI"].between(0, 100).all()
    
    # Test Bollinger Bands
    assert "BB_Upper" in data.columns
    assert "BB_Lower" in data.columns
    assert (data["BB_Upper"] >= data["BB_Lower"]).all()
```

## Test Data

Use `conftest.py` for shared test fixtures:

```python
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def sample_price_data():
    dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
    prices = np.random.randn(len(dates)).cumsum() + 100
    return pd.Series(prices, index=dates)

@pytest.fixture
def sample_portfolio():
    return {
        "AAPL": {"quantity": 100, "price": 150},
        "MSFT": {"quantity": 50, "price": 300},
        "GOOGL": {"quantity": 25, "price": 2500}
    }
```