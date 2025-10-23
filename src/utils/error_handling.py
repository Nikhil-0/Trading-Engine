import time
from functools import wraps
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

def retry(max_retries: int = 3, 
         delay: float = 1.0, 
         backoff_factor: float = 2.0, 
         exceptions: tuple = (Exception,)) -> Callable:

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
            return None
        return wrapper
    return decorator

# Base exception for trading engine errors
class TradingEngineError(Exception):
    pass

# Error when fetching market data
class DataFetchError(TradingEngineError):
    pass

# Error in strategy execution
class StrategyError(TradingEngineError):
    pass

# Error in trade execution
class ExecutionError(TradingEngineError):
    pass

# Error in data validation
class ValidationError(TradingEngineError):
    pass