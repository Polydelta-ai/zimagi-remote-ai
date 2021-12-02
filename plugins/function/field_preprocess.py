from systems.plugins.index import BaseProvider
from systems.remote_ai.preprocessor import Preprocessor


class Provider(BaseProvider('function', 'field_preprocess')):

    def exec(self, data, field_data):
        return field_data.apply(Preprocessor.run)
