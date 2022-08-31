import abc
from collections import UserDict, OrderedDict
from typing import Callable


class BaseStrategy(abc.ABC):
    """Base class for all types of all individual strategies"""

    def __str__(self):
        return f'{self.name} ({self.year})' if self.year else self.name

    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    def year(self) -> int:
        return 0

    @property
    def reference(self) -> str:
        return ''


class BaseStrategies(UserDict, abc.ABC):
    """Abstract class holding individual strategies as a name: strategy dict."""

    strategy_type = BaseStrategy
    default: strategy_type = None
    registry: OrderedDict

    @abc.abstractmethod
    def registry(self) -> dict:
        raise NotImplementedError

    @classmethod
    def create(cls, name: str = '') -> strategy_type:
        strategy_class = cls.registry[name] if name else cls.default
        return strategy_class()

    @classmethod
    def register(cls, default: bool = False) -> Callable:
        def decorator(decorated_strategy: cls.strategy_type)\
                -> cls.strategy_type:
            name = decorated_strategy.name
            if name in cls.registry:
                raise KeyError(f'{name} already registered in {cls.__name__}')
            if default:
                if cls.default is not None:
                    raise ValueError(f'2nd default {name} for {cls.__name__}')
                cls.default = decorated_strategy
            cls.registry[name] = decorated_strategy
            return decorated_strategy
        return decorator
