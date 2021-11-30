from systems.commands.index import CommandMixin


class RemoteAIMixin(CommandMixin('remote_ai')):

    def get_dataset(self):
        if self.data_name:
            return self.get_instance(self._dataset, self.data_name).provider.load()
        return None
