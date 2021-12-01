from systems.commands.index import CommandMixin


class RemoteAITrainingMixin(CommandMixin('remote_ai_training')):

    def predictor_field(self):
        raise NotImplementedError("Implement predictor_field in derived classes of the Machine Learning Training Mixin")

    def target_field(self):
        raise NotImplementedError("Implement target_field in derived classes of the Machine Learning Training Mixin")


    def exec(self):
        self.run_model(self.get_dataset())

    def run_model(self, dataset):
        model = self.init_model()

        training_data, test_data = model.split_data(
            dataset,
            training_percentage = self.training_percentage,
            shuffle = self.shuffle_data
        )
        training_results = self.train(model, training_data)
        test_results = self.predict(model, test_data)
        return model, training_results, test_results


    def init_model(self):
        model_params = self.model_parameters()
        model_params['predictor_field'] = self.predictor_field()
        model_params['target_field'] = self.target_field()

        model = self.get_model(self.model_name, model_params)

        self.notice('Loading or building model')
        model.load()
        return model

    def model_parameters(self):
        return {}


    def train(self, model, dataset):
        self.notice('Training model')
        return model.train(dataset, **self.train_parameters())

    def train_parameters(self):
        return {}


    def predict(self, model, dataset):
        self.notice('Running test predictions and generating results')
        test_results = model.predict(dataset, **self.predict_parameters())
        return test_results

    def predict_parameters(self):
        return {}
