from systems.plugins.index import BaseProvider


class Provider(BaseProvider('function', 'data_combined_text')):

    def exec(self, data, field_data, append = None, separator = "\n"):
        if append:
            for field in append.split(','):
                field_data = field_data.str.cat(
                    data[field].astype(str),
                    sep = separator
                )

        return field_data
