from sklearn.utils import shuffle
from django.conf import settings

from systems.plugins.index import BasePlugin
from utility.time import Time
from utility.project import project_dir
from utility.dataframe import get_csv_file_name

import math


class BaseProvider(BasePlugin('remote_ai_model')):

    def __init__(self, type, name, command, model_name, model_config):
        super().__init__(type, name, command)

        model_config['model_name'] = model_name
        self.import_config(model_config)

        self.time_processor = Time(
            settings.DEFAULT_DATE_FORMAT,
            settings.DEFAULT_TIME_FORMAT,
            settings.DEFAULT_TIME_SPACER_FORMAT
        )

        self.model = None
        self.timestamp = self.time_processor.now


    @property
    def model_id(self):
        return self.field_model_name


    @property
    def _model_project(self):
        return project_dir(settings.REMOTE_AI_PROJECT_NAME, settings.REMOTE_AI_PROJECT_MODEL_DIR)

    @property
    def _result_project(self):
        return project_dir(settings.REMOTE_AI_PROJECT_NAME, settings.REMOTE_AI_PROJECT_RESULT_DIR)


    def load(self):
        with self._model_project as project:
            model_path = project.path(self.model_id)

            if project.exists(self.model_id):
                self.model = self.load_model(model_path)
            else:
                self.build()
        return self.model

    def build(self):
        self.model = self.build_model()
        self.save()

    def load_model(self, model_path):
        raise NotImplementedError("Implement load_model in derived classes of the base Machine Learning Model provider")

    def build_model(self):
        raise NotImplementedError("Implement build_model in derived classes of the base Machine Learning Model provider")


    def save(self):
        with self._model_project as project:
            self.save_model(project.path(self.model_id))

    def save_model(self, model_path):
        raise NotImplementedError("Implement save_model in derived classes of the base Machine Learning Model provider")


    def train(self, dataset, **params):
        raise NotImplementedError("Implement train in derived classes of the base Machine Learning Model provider")

    def predict(self, dataset, **params):
        raise NotImplementedError("Implement train in derived classes of the base Machine Learning Model provider")


    def export(self, name, data, **options):
        with self._result_project as project:
            project.save(
                data.to_csv(date_format = self.time_processor.time_format, **options),
                get_csv_file_name("{}_{}".format(self.model_id, name))
            )


    def split_data(self, dataset, training_percentage = 0.75, shuffle = True):

        def normalize(data):
            return data.fillna(0)

        sample_data = list()
        percentages = [ training_percentage, 100 - training_percentage ]
        index = 0

        dataset = dataset.drop_duplicates()

        if shuffle:
            dataset = shuffle(dataset)

        for percentage in percentages:
            length = math.floor(dataset.shape[0] * percentage)
            sample_data.append(normalize(dataset[index:(index + length)]))
            index += length

        return sample_data[0], sample_data[1]
