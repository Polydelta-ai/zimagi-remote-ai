from django.conf import settings
from sklearn.svm import SVC

from systems.plugins.index import BaseProvider
from systems.remote_ai.tfidf_trainer import TfidfTrainer


class Provider(BaseProvider('remote_ai_model', 'tdidf_svc')):

    def tfidf_processor_class(self):
        return TfidfTrainer


    def init_model(self):
        self.tfidf_trainer = self.tfidf_processor_class()(self)

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


    def classify_prediction(self, prediction):
        classification = None

        if prediction >= settings.REMOTE_AI_PREDICTION_THRESHOLD:
            if prediction >= settings.REMOTE_AI_PREDICTION_HIGH_CONFIDENCE:
                classification = 'ELIGIBLE high confidence'
            else:
                classification = 'ELIGIBLE medium confidence'

        elif 1 - prediction >= settings.REMOTE_AI_PREDICTION_THRESHOLD:
            if 1 - prediction >= settings.REMOTE_AI_PREDICTION_HIGH_CONFIDENCE:
                classification = 'INELIGIBLE high confidence'
            else:
                classification = 'INELIGIBLE medium confidence'

        return classification
