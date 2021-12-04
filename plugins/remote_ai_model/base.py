from django.conf import settings
from sklearn.metrics import precision_score, recall_score, f1_score

from systems.plugins.index import BasePlugin
from utility.time import Time
from utility.project import project_dir
from utility.dataframe import get_csv_file_name

import pickle
import math
import pandas


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
            self._load()

    def store_related(self, instance, created, test):
        self._load()
        self._train(save = not test)

    def finalize_instance(self, instance):
        self._remove()


    def get_model_project(self):
        return project_dir(settings.REMOTE_AI_PROJECT_NAME, settings.REMOTE_AI_PROJECT_MODEL_DIR)

    def get_result_project(self):
        return project_dir(settings.REMOTE_AI_PROJECT_NAME, settings.REMOTE_AI_PROJECT_RESULT_DIR)


    def model_file(self):
        return "{}_{}".format(self.name, self.instance.name)


    def _load(self):
        if not self.model:
            self.instance.dataset.initialize(self.command)

            with self.get_model_project() as project:
                if project.exists(self.model_file()):
                    self.model = self.load_model(project)
                else:
                    self._build()

            self.init_model()

        return self.model

    def init_model(self):
        # Override in sub class if needed
        pass

    def load_model(self, project):
        with open(project.path(self.model_file()), "rb") as file:
            return pickle.load(file)

    def _build(self):
        self.model = self.build_model()
        self._save()

    def build_model(self):
        raise NotImplementedError("Implement build_model in derived classes of the base Machine Learning Model provider")


    def _save(self):
        self.command.notice("Saving {} model: {}".format(self.name, self.instance.name))
        with self.get_model_project() as project:
            self.save_model(project)

    def save_model(self, project):
        with open(project.path(self.model_file()), "wb") as file:
            pickle.dump(self.model, file)


    def _remove(self):
        self.command.notice("Removing {} model: {}".format(self.name, self.instance.name))
        with self.get_model_project() as project:
            self.remove_model(project)

    def remove_model(self, project):
        project.remove(self.model_file(project.path(self.instance.name)))


    def _split_data(self, dataset):
        sample_data = list()
        percentages = [ self.instance.training_percentage, 1 - self.instance.training_percentage ]
        index = 0

        for percentage in percentages:
            if percentage > 0:
                length = math.floor(dataset.shape[0] * percentage)
                sample_data.append(dataset[index:(index + length)])
                index += length
            else:
                sample_data.append(None)

        return sample_data[0], sample_data[1]


    def _train(self, save = True):
        if self.instance.dataset is not None:
            dataset = self.instance.dataset.provider.load()

            self.command.notice("Training {} model {}".format(self.name, self.instance.name))
            training_data, test_data = self._split_data(dataset)

            self.train_model(
                training_data[self.field_predictor],
                training_data[self.field_target]
            )
            if self.instance.training_percentage < 1:
                self.calculate_performance(
                    pandas.DataFrame({
                        'predictions': self.predict(test_data[self.field_predictor], False)
                    }),
                    test_data[self.field_target]
                )
                self.command.success("Model performance")
                self.command.data('Precision', self.instance.precision)
                self.command.data('Recall', self.instance.recall)
                self.command.data('F1 score', self.instance.f1_score)

            if save:
                self._save()

    def train_model(self, predictors, targets):
        raise NotImplementedError("Implement train_model in derived classes of the base Machine Learning Model provider")

    def calculate_performance(self, predictions, targets):
        predictions = self.normalize_predictions(predictions)

        self.instance.precision = precision_score(targets, predictions)
        self.instance.recall = recall_score(targets, predictions)
        self.instance.f1_score = f1_score(targets, predictions)
        self.instance.save()

    def normalize_predictions(self, predictions):
        # Override in providers if needed
        return predictions


    def predict(self, data, display_prediction_input = True):
        results = None

        if data is not None:
            multiple = True

            self.command.notice("Predicting with {} model {}{}".format(
                self.name,
                self.instance.name,
                " given: {}".format(data) if display_prediction_input else ''
            ))

            if isinstance(data, tuple):
                data = list(data)
            elif isinstance(data, (pandas.DataFrame, pandas.Series)):
                data = data.tolist()
            elif not isinstance(data, list):
                data = [data]
                multiple = False

            results = self.predict_model(data)
            if not multiple:
                results = results[0]

        return results

    def predict_model(self, data):
        raise NotImplementedError("Implement predict_model in derived classes of the base Machine Learning Model provider")


    def export(self, name, data, **options):
        with self.get_result_project() as project:
            project.save(
                data.to_csv(date_format = self.time_processor.time_format, **options),
                get_csv_file_name("{}_{}_{}".format(self.name, self.instance.name, name))
            )
