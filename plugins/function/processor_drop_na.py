from systems.plugins.index import BaseProvider


class Provider(BaseProvider('function', 'processor_drop_na')):

    def exec(self, dataset):
        return dataset.dropna()
