from strategies import StealingStrategy


class Thief():

    def __init__(self, strategy: StealingStrategy):
        self._strategy: StealingStrategy = strategy

    @property
    def strategy(self) -> StealingStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy):
        self._strategy = strategy

    def get_images_list(self, *args):
        result = {}
        for a in args:
            res = self._strategy.get_images(a[0], a[1])
            result[a[0]] = res
        return result
