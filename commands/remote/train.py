from systems.commands.index import Command


class Train(Command('remote.train')):

    def exec(self):
        self.success("Training remote!")
