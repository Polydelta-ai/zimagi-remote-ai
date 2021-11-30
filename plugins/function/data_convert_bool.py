from systems.plugins.index import BaseProvider


class Provider(BaseProvider('function', 'data_convert_bool')):

    def exec(self, data, field_data):
        return field_data.map({ True: 1, False: 0 })
