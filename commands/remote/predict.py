from django.conf import settings

from systems.commands.index import Command
from systems.remote_ai.preprocessor import Preprocessor


class Predict(Command('remote.predict')):

    def exec(self):
        model = self.remote_ai_model
        record = self._remote_ai_prediction.create(None,
            remote_ai_model = model,
            job_text = self.job_text
        )
        record.prediction = model.provider.predict(
            Preprocessor.run(self.job_text)
        )
        record.threshold_diff = (record.prediction - settings.REMOTE_AI_PREDICTION_THRESHOLD)
        record.classification = self.classify_prediction(record.prediction)

        record.save()
        self.data("Prediction", record.prediction, 'prediction')
        self.data("Classification", str(record.classification), 'classification')


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
