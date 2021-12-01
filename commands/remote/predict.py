from systems.commands.index import Command


class Predict(Command('remote.predict')):

    def predictor_field(self):
        return 'job_combined_text'

    def target_field(self):
        return 'job_telework_eligible'


    def exec(self):
        self.success("Predicting remote!")
