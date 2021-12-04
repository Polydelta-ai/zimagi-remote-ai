from systems.plugins.index import BaseProvider
from systems.remote_ai.preprocessor import Preprocessor


class Provider(BaseProvider('field_processor', 'preprocess')):

    def exec(self, dataset, field_data):
        return field_data.apply(Preprocessor.run)
