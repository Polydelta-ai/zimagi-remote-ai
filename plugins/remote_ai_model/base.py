from django.conf import settings

from systems.plugins.index import BasePlugin
from utility.time import Time
from utility.project import project_dir
from utility.dataframe import get_csv_file_name

import math


class BaseProvider(BasePlugin('remote_ai_model')):

    def __init__(self, type, name, command, instance = None):
        super().__init__(type, name, command, instance)

        self.model = None
        self.time_processor = Time(
            settings.DEFAULT_DATE_FORMAT,
            settings.DEFAULT_TIME_FORMAT,
            settings.DEFAULT_TIME_SPACER_FORMAT
        )
        if instance:
            self._load(instance)

    def store_related(self, instance, created, test):
        self.instance = instance

        self._load(instance)
        self._train(instance, save = not test)

    def finalize_instance(self, instance):
        self._remove(instance)


    def get_model_project(self):
        return project_dir(settings.REMOTE_AI_PROJECT_NAME, settings.REMOTE_AI_PROJECT_MODEL_DIR)

    def get_result_project(self):
        return project_dir(settings.REMOTE_AI_PROJECT_NAME, settings.REMOTE_AI_PROJECT_RESULT_DIR)


    def model_file(self, project_path, instance):
        return "{}_{}_{}".format(project_path, self.name, instance.name)


    def _load(self, instance):
        if not self.model:
            with self.get_model_project() as project:
                model_path = project.path(instance.name)

                if project.exists(self.model_file(model_path, instance)):
                    self.model = self.load_model(project, instance)
                else:
                    self._build(instance)

            self.init_model(instance)

        return self.model

    def init_model(self, instance):
        # Override in sub class if needed
        pass

    def load_model(self, project, instance):
        raise NotImplementedError("Implement load_model in derived classes of the base Machine Learning Model provider")

    def _build(self, instance):
        self.model = self.build_model(instance)
        self._save(instance)

    def build_model(self, instance):
        raise NotImplementedError("Implement build_model in derived classes of the base Machine Learning Model provider")


    def _save(self, instance):
        self.command.notice("Saving {} model: {}".format(self.name, instance.name))
        with self.get_model_project() as project:
            self.save_model(project, instance)

    def save_model(self, project, instance):
        raise NotImplementedError("Implement save_model in derived classes of the base Machine Learning Model provider")


    def _remove(self, instance):
        self.command.notice("Removing {} model: {}".format(self.name, instance.name))
        with self.get_model_project() as project:
            self.remove_model(project, instance)

    def remove_model(self, project, instance):
        project.remove(self.model_file(project.path(instance.name), instance))


    def split_data(self, dataset, training_percentage = 1):
        sample_data = list()
        percentages = [ training_percentage, 1 - training_percentage ]
        index = 0

        for percentage in percentages:
            if percentage > 0:
                length = math.floor(dataset.shape[0] * percentage)
                sample_data.append(dataset[index:(index + length)])
                index += length
            else:
                sample_data.append(None)

        return sample_data[0], sample_data[1]


    def _train(self, instance, save = True):
        results = None
        dataset = instance.dataset.provider.load()

        if dataset is not None:
            self.command.notice("Training {} model {}".format(self.name, instance.name))
            results = self.train_model(instance, dataset)

            if save:
                self._save(instance)

        return results

    def train_model(self, instance, dataset):
        raise NotImplementedError("Implement train in derived classes of the base Machine Learning Model provider")


    def predict(self, data):
        instance = self.check_instance('predict')
        results = None

        if data is not None:
            self.command.notice("Predicting with {} model {} given: {}".format(
                self.name,
                instance.name,
                data
            ))
            results = self.predict_model(instance, data)

        return results

    def predict_model(self, instance, data):
        raise NotImplementedError("Implement train in derived classes of the base Machine Learning Model provider")


    def export(self, name, data, **options):
        instance = self.check_instance('export')

        with self.get_result_project() as project:
            project.save(
                data.to_csv(date_format = self.time_processor.time_format, **options),
                get_csv_file_name("{}_{}_{}".format(self.name, instance.name, name))
            )
