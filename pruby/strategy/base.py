from collections import OrderedDict


class Strategy:
    dict = OrderedDict()

    def __new__(cls, name):
        return cls.dict[name]()

    @classmethod
    def subscribe(cls, strategy):
        cls.dict[strategy.name] = strategy

    @property
    def default(self):
        return next(iter(self.dict))
