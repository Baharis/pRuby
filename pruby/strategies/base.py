import abc
from collections import UserDict
from typing import Callable


class BaseStrategy(abc.ABC):
    """Base class for all types of all individual strategies"""
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError


class BaseStrategies(UserDict, abc.ABC):
    """Abstract class holding individual strategies as a name: strategy dict."""

    default: BaseStrategy
    registry = {}

    @classmethod
    def create(cls, name: str = '') -> BaseStrategy():
        strategy_class = cls.registry[name] if name else cls.default
        return strategy_class()

    @classmethod
    def register(cls, default: bool = False) -> Callable:
        def decorator(decorated_strategy: BaseStrategy) -> BaseStrategy:
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
