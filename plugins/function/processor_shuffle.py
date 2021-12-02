from sklearn.utils import shuffle

from systems.plugins.index import BaseProvider


class Provider(BaseProvider('function', 'processor_shuffle')):

    def exec(self, dataset):
        return shuffle(dataset)
