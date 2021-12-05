from django.conf import settings

from systems.commands.index import Command
from systems.remote_ai.preprocessor import Preprocessor


class Predict(Command('remote.predict')):

    def exec(self):
        model = self.find_remote_ai_model()
        record = self._remote_ai_prediction.create(None,
            remote_ai_model = model,
            job_text = self.job_text
        )
        record.prediction = model.provider.predict(
            Preprocessor.run(self.job_text)
        )
        record.threshold_diff = (record.prediction - settings.REMOTE_AI_PREDICTION_THRESHOLD)
        record.classification = model.provider.classify_prediction(record.prediction)

        record.save()
        self.data("Prediction", record.prediction, 'prediction')
        self.data("Classification", str(record.classification), 'classification')
