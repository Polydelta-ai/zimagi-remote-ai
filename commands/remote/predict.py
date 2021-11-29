from systems.commands.index import Command


class Predict(Command('remote.predict')):

    def exec(self):
        self.success("Predicting remote!")
