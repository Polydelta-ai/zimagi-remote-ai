from systems.commands.index import CommandMixin


class RemoteAIMixin(CommandMixin('remote_ai')):

    def get_dataset(self):
        if self.data_name:
            return self.get_instance(self._dataset, self.data_name).provider.load()
        return None


    def get_model(self, name, model_params):
        return self.get_provider('remote_ai_model',
            self.model_provider_name,
            name, model_params
        )
