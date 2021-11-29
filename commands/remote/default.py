from systems.commands.index import Command


class Default(Command('remote.default')):

    def exec(self):
        self.success("Setting default model!")
