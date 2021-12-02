from sklearn.svm import SVC

from systems.plugins.index import BaseProvider
from systems.remote_ai.tfidf_trainer import TfidfTrainer

import pickle


class Provider(BaseProvider('remote_ai_model', 'tdidf_svc')):

    def tfidf_processor_class(self):
        return TfidfTrainer


    def init_model(self, instance):
        self.tfidf_trainer = self.tfidf_processor_class()(self)

    def load_model(self, project, instance):
        with open(self.model_file(project.path(instance.name), instance), "rb") as file:
            return pickle.load(file)

    def save_model(self, project, instance):
        with open(self.model_file(project.path(instance.name), instance), "wb") as file:
            pickle.dump(self.model, file)

    def build_model(self, instance):
        return SVC(
            kernel = "linear",
            probability = True,
            random_state = 1234
        )


    def train_model(self, instance, dataset):
        self.command.notice("Fitting {} model {} TFIDF trainer".format(self.name, instance.name))
        self.tfidf_trainer.fit(dataset[self.field_predictor])

        self.command.notice("Fitting {} model {} classifications".format(self.name, instance.name))
        return self.model.fit(
            self.tfidf_trainer.transform(dataset[self.field_predictor]),
            dataset[self.field_target]
        )

    def predict_model(self, instance, data):
        multiple = True

        if isinstance(data, (tuple, list)):
            data = list(data)
        elif isinstance(data, str):
            data = [data]
            multiple = False
        else:
            data = data[self.field_predictor]

        results = self.model.predict_proba(
            self.tfidf_trainer.transform(data)
        )[:, 1]
        return results if multiple else results[0]
