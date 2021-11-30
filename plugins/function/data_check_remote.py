from systems.plugins.index import BaseProvider


class Provider(BaseProvider('function', 'data_check_remote')):

    def exec(self, data, field_data, test):
        field_data = field_data.str.contains(test)
        return field_data.map({ True: 1, False: 0 })
