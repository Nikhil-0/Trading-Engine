import yaml
from typing import Dict, Any
import os
from dotenv import load_dotenv

class Config:
    def __init__(self, config_path: str = 'config.yaml'):
        self.config_path = config_path
        self.config = self._load_config()
        self._load_environment()
    
    def _load_config(self) -> Dict[str, Any]:

        if not os.path.exists(self.config_path):
            return self._create_default_config()
        
        with open(self.config_path, 'r') as file:
            return yaml.safe_load(file)
    
    def _create_default_config(self) -> Dict[str, Any]:

        config = {
            'data': {
                'default_source': 'yahoo',
                'cache_dir': 'data/cache',
                'history_start': '2010-01-01'
            },
            'backtesting': {
                'initial_capital': 100000,
                'commission': 0.001,
                'slippage': 0.001
            },
            'risk_management': {
                'max_position_size': 0.1,
                'stop_loss': 0.02,
                'take_profit': 0.05,
                'max_drawdown': 0.25
            },
            'logging': {
                'level': 'INFO',
                'file_path': 'logs/trading_engine.log'
            }
        }
        
        with open(self.config_path, 'w') as file:
            yaml.dump(config, file)
        
        return config
    
    def _load_environment(self) -> None:
        load_dotenv()
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
                
        return value if value is not None else default
    
    def set(self, key: str, value: Any) -> None:
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            config = config.setdefault(k, {})
            
        config[keys[-1]] = value
        
        with open(self.config_path, 'w') as file:
            yaml.dump(self.config, file)