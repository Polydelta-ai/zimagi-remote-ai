from systems.commands.index import Command


class Train(Command('remote.train')):

    def predictor_field(self):
        return 'job_combined_text'

    def target_field(self):
        return 'job_telework_eligible'
