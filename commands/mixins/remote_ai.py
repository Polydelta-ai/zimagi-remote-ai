from django.conf import settings

from systems.commands.index import CommandMixin


class RemoteAIMixin(CommandMixin('remote_ai')):

    def find_remote_ai_model(self):
        if self.remote_ai_model_name:
            model = self.remote_ai_model
        else:
            filters = {}

            if self.model_groups:
                filters['groups__name__in'] = self.model_groups

            filters['training_percentage__range'] = [
                self.training_percentage_min,
                self.training_percentage_max
            ]

            model = self._remote_ai_model.set_order(
                "-{}".format(self.metric_field)
            ).filter(**filters)[0]
            model.initialize(self)

        return model


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