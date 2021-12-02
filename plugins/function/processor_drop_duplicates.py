from systems.plugins.index import BaseProvider


class Provider(BaseProvider('function', 'processor_drop_duplicates')):

    def exec(self, dataset):
        return dataset.drop_duplicates()
