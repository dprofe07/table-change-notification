import copy


def prepare_dict(selected, base):
    res = copy.deepcopy(base)
    for k in selected.keys():
        if isinstance(selected[k], dict):
            res[k] = prepare_dict(selected[k], res[k])
        else:
            res[k] = selected[k]
    return res

def fail_if(data: bool, error_text: str=""):
    if data:
        raise ValueError(error_text)

class TableData:
    def __init__(self, data, table_name):
        self.table_name = table_name
        self.data = data

        self.table_key = self.load_column('table-key')
        self.first_task_column = self.load_column('first-task-column')
        self.names_column = self.load_column('names-column')
        self.tasks_row = self.load_column('tasks-row')
        self.task_number_type = self.load_column('task-number')
        self.statuses = self.load_column('statuses')
        self.worksheet_picking_type = self.load_column('worksheet')
        self.tasks_url = self.load_column('tasks-url', True)

    def load_column(self, column_name, nullable=False):
        data = (
                self.data[self.table_name].get(column_name) or
                self.data['$default'].get(column_name) or
                fail_if(not nullable, f"field {column_name} cannot be null")
        )
        if isinstance(data, dict):
            return prepare_dict(data, self.data['$default'].get(column_name))
        return data
