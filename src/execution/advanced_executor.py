import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from datetime import datetime
import ccxt
from ..utils.logger import setup_logger
from ..utils.config import Config

logger = setup_logger(__name__)
config = Config()

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class Order:
    def __init__(self,
                 symbol: str,
                 order_type: OrderType,
                 side: OrderSide,
                 quantity: float,
                 price: Optional[float] = None,
                 stop_price: Optional[float] = None,
                 trailing_percent: Optional[float] = None):
        self.symbol = symbol
        self.order_type = order_type
        self.side = side
        self.quantity = quantity
        self.price = price
        self.stop_price = stop_price
        self.trailing_percent = trailing_percent
        self.status = "pending"
        self.filled_quantity = 0
        self.filled_price = 0
        self.timestamp = datetime.now()

class ExecutionHandler:
    def __init__(self,
                 commission: float = 0.001,
                 slippage: float = 0.001,
                 exchange_id: str = "binance"):
        self.commission = commission
        self.slippage = slippage
        self.positions = {}
        self.orders = []
        self.trades = []
        self.exchange = None
        self.exchange_id = exchange_id
        
        # Initialize exchange connection for live trading
        if config.get('trading.mode') == 'live':
            self._initialize_exchange()

    # Initialize connection to cryptocurrency exchange
    def _initialize_exchange(self) -> None:
        try:
            exchange_class = getattr(ccxt, self.exchange_id)
            self.exchange = exchange_class({
                'apiKey': config.get('exchange.api_key'),
                'secret': config.get('exchange.api_secret'),
                'enableRateLimit': True
            })
        except Exception as e:
            logger.error(f"Failed to initialize exchange: {e}")
            raise
    
    def create_order(self,
                    symbol: str,
                    order_type: OrderType,
                    side: OrderSide,
                    quantity: float,
                    price: Optional[float] = None,
                    stop_price: Optional[float] = None,
                    trailing_percent: Optional[float] = None) -> Order:
        
        # Create a new order
        order = Order(
            symbol=symbol,
            order_type=order_type,
            side=side,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            trailing_percent=trailing_percent
        )
        
        if config.get('trading.mode') == 'live':
            self._execute_live_order(order)
        else:
            self._execute_simulated_order(order)
        
        self.orders.append(order)
        return order
    
    def _execute_live_order(self, order: Order) -> None:
        try:
            params = {}
            if order.order_type == OrderType.TRAILING_STOP:
                params['trailing_percent'] = order.trailing_percent
            
            response = self.exchange.create_order(
                symbol=order.symbol,
                type=order.order_type.value,
                side=order.side.value,
                amount=order.quantity,
                price=order.price,
                params=params
            )
            
            order.status = "filled"
            order.filled_quantity = order.quantity
            order.filled_price = response['price']
            
            self._update_positions(order)
            self._record_trade(order)
            
        except Exception as e:
            logger.error(f"Failed to execute live order: {e}")
            order.status = "failed"
            raise
    
    def _execute_simulated_order(self, order: Order) -> None:
        # Simulate slippage
        slippage_factor = 1 + (self.slippage * (1 if order.side == OrderSide.BUY else -1))
        
        if order.order_type == OrderType.MARKET:
            order.filled_price = order.price * slippage_factor
            order.status = "filled"
            order.filled_quantity = order.quantity
            
        elif order.order_type == OrderType.LIMIT:
            if ((order.side == OrderSide.BUY and order.price >= order.stop_price) or
                (order.side == OrderSide.SELL and order.price <= order.stop_price)):
                order.filled_price = order.price
                order.status = "filled"
                order.filled_quantity = order.quantity
            else:
                order.status = "pending"
                
        self._update_positions(order)
        self._record_trade(order)
    
    def _update_positions(self, order: Order) -> None:
        if order.status != "filled":
            return
            
        position = self.positions.get(order.symbol, {
            'quantity': 0,
            'average_price': 0,
            'realized_pnl': 0
        })
        
        if order.side == OrderSide.BUY:
            # Update average price and quantity
            total_cost = (position['quantity'] * position['average_price'] +
                         order.filled_quantity * order.filled_price)
            new_quantity = position['quantity'] + order.filled_quantity
            position['average_price'] = total_cost / new_quantity if new_quantity > 0 else 0
            position['quantity'] = new_quantity
            
        else:  # SELL
            # Calculate realized PnL
            pnl = (order.filled_price - position['average_price']) * order.filled_quantity
            position['realized_pnl'] += pnl
            position['quantity'] -= order.filled_quantity
            
        if position['quantity'] == 0:
            del self.positions[order.symbol]
        else:
            self.positions[order.symbol] = position
    
    def _record_trade(self, order: Order) -> None:
        if order.status != "filled":
            return
            
        trade = {
            'timestamp': order.timestamp,
            'symbol': order.symbol,
            'order_type': order.order_type.value,
            'side': order.side.value,
            'quantity': order.filled_quantity,
            'price': order.filled_price,
            'commission': order.filled_quantity * order.filled_price * self.commission
        }
        
        self.trades.append(trade)
    
    def get_position(self, symbol: str) -> Dict[str, Any]:
        return self.positions.get(symbol, {
            'quantity': 0,
            'average_price': 0,
            'realized_pnl': 0
        })
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        open_orders = [order for order in self.orders if order.status == "pending"]
        if symbol:
            open_orders = [order for order in open_orders if order.symbol == symbol]
        return open_orders
    
    def cancel_order(self, order: Order) -> bool:
        if order.status != "pending":
            return False
            
        if config.get('trading.mode') == 'live':
            try:
                self.exchange.cancel_order(order.id, order.symbol)
            except Exception as e:
                logger.error(f"Failed to cancel order: {e}")
                return False
                
        order.status = "cancelled"
        return True
    
    def get_trade_history(self) -> pd.DataFrame:
        return pd.DataFrame(self.trades)
    
    def calculate_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        portfolio_value = 0
        
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                market_value = position['quantity'] * current_prices[symbol]
                portfolio_value += market_value
                
        return portfolio_value