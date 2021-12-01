from sklearn.svm import SVC

from systems.plugins.index import BaseProvider
from systems.remote_ai.tfidf_trainer import TfidfTrainer

import pickle


class Provider(BaseProvider('remote_ai_model', 'tdidf_svc')):

    def model_file(self, model_path):
        return "{}-{}".format(model_path, 'classifier_model.pk')


    def load(self):
        with self._model_project as project:
            model_path = project.path(self.model_id)

            if project.exists(self.model_file(model_path)):
                self.model = self.load_model(model_path)
            else:
                self.build()
        return self.model

    def load_model(self, model_path):
        with open(self.model_file(model_path), "rb") as file:
            return pickle.load(file)

    def build_model(self):
        return SVC(kernel = "linear", probability = True, random_state = 1234)

    def save_model(self, model_path):
        with open(self.model_file(model_path), "wb") as file:
            pickle.dump(self.model, file)


    def train(self, dataset, **params):
        tfidf_module = TfidfTrainer(self)
        tfidf_module.fit(dataset[self.field_predictor_field])

        results = self.model.fit(
            tfidf_module.transform(dataset[self.field_predictor_field]),
            dataset[self.field_target_field]
        )
        self.save()
        return results

    def predict(self, dataset, **params):
        return self.model.predict_proba(dataset[self.field_predictor_field])
