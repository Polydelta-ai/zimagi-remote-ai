from django.conf import settings
from sklearn.svm import SVC

from systems.plugins.index import BaseProvider
from systems.remote_ai.tfidf_trainer import TfidfTrainer

import pickle


class Provider(BaseProvider('remote_ai_model', 'tdidf_svc')):

    def tfidf_processor_class(self):
        return TfidfTrainer


    def init_model(self):
        self.tfidf_trainer = self.tfidf_processor_class()(self)

    def load_model(self, project):
        with open(project.path(self.model_file()), "rb") as file:
            return pickle.load(file)

    def save_model(self, project):
        with open(project.path(self.model_file()), "wb") as file:
            pickle.dump(self.model, file)

    def build_model(self):
        return SVC(
            probability = True,
            kernel = self.field_kernel,
            random_state = self.field_random_state
        )


    def train_model(self, predictors, targets):
        self.command.notice("Fitting TFIDF trainer")
        self.tfidf_trainer.fit(predictors)

        self.command.notice("Fitting classification model")
        self.model.fit(
            self.tfidf_trainer.transform(predictors),
            targets
        )

    def predict_model(self, data):
        return self.model.predict_proba(
            self.tfidf_trainer.transform(data)
        )[:, 1]

    def normalize_predictions(self, predictions):
        predictions = predictions > settings.REMOTE_AI_PREDICTION_THRESHOLD
        return predictions.astype(int)
