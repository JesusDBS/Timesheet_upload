import csv
import datetime
import time
import xlsxwriter
from typing import Any
from collections import deque


class Spreadsheet:
    """This class creates a spreadsheet for uploading timesheet to Odoo
    """
    format = "%Y-%m-%d"

    def __init__(self) -> None:
        self.__date = datetime.datetime.today().strftime(self.format)
        self.__data = dict()
        self.__columns_to_rename = dict()

    @property
    def date(self):
        """Date for the spreadsheet name
        """
        return self.__date

    @date.setter
    def date(self, value):
        if isinstance(value, str):
            try:
                date = datetime.datetime.strptime(value, self.format)
                self.__date = date
                return self.__date

            except ValueError:
                raise ValueError(
                    f"Your date: '{value}' does not match the format required {self.format}. Please check it.")

    @property
    def columns_to_rename(self):
        """Columns to rename in the spreadsheet
        """
        return self.__columns_to_rename

    @columns_to_rename.setter
    def columns_to_rename(self, value):
        if isinstance(value, dict):
            self.__columns_to_rename = value
            return self.__columns_to_rename

        raise ValueError(
            f'columns_to_rename: {value} must be a list of tuples!')

    def _create_workbook(self):
        self.workbook = xlsxwriter.Workbook(f'timesheets_{self.date}.xlsx')
        self.worksheet = self.workbook.add_worksheet()

    # TODO refactor this method and try to create the workbook inheritating from Workbook class
    def create_workbook(self):
        """Creates the workbook
        """
        self._create_workbook()
        timesheets = self._transform_data()

        row = 0
        col = 0

        for fields in timesheets:
            self.worksheet.write(row, col, fields[0])
            self.worksheet.write(row, col + 1, fields[1])
            self.worksheet.write(row, col + 2, fields[2])
            self.worksheet.write(row, col + 3, fields[3])
            self.worksheet.write(row, col + 4, fields[4])
            row += 1

        self.workbook.close()

    @property
    def data(self):
        """Data for spreadsheet creation
        """
        return self.__data

    @data.setter
    def data(self, value):
        if isinstance(value, dict):
            self.__data = value
            return self.__data

        raise ValueError(f'Data must be a dictionary!')

    def _transform_data(self) -> list:
        """Transform data dict to data format for write spreadsheet
        """
        columns = self.__get_columns(
            keys_to_rename=self.columns_to_rename,
            data=self.data
        )
        rows = self._get_rows(data=self.data)
        rows.append(columns)
        rows = self._rotate_row_list(rows)

        return rows

    @staticmethod
    def _rotate_row_list(rows: list, n: int = 1) -> list:
        """Rotates the row list
        """
        rows = deque(rows)
        rows.rotate(n)
        rows = list(rows)

        return rows

    @staticmethod
    def __get_columns(keys_to_rename: dict, data: dict) -> list:
        """Get columns for spreadsheet
        """
        keys = list()

        for key in data.keys():
            key = key.capitalize()
            if key in keys_to_rename.keys():
                keys.append(keys_to_rename[key])
            else:
                keys.append(key.lower())

        return keys

    @staticmethod
    def _get_rows(data: dict) -> list:
        """Get rows for spreadsheet
        """
        rows = list()

        for _, val in data.items():
            rows.append(val)

        rows = list(zip(*rows))
        return list(map(list, rows))


class TimesheetPipeline:
    """This class takes a csv file and transform it into a excel file for uploading daily timesheets to Odoo
    """
    format = "%Y-%m-%d"

    def __init__(self, path: str,
                 keys_to_remove: list = [],
                 columns_to_rename: dict = {},
                 project_ids: dict = {},
                 sep='') -> None:
        self.path = path
        self.keys_to_remove = keys_to_remove
        self.columns_to_rename = columns_to_rename
        self.project_ids = project_ids
        self.sep = sep
        self.__activities_date = datetime.datetime.today()
        self.spreadsheet = Spreadsheet()

    @property
    def activities_date(self):
        """Dates when the activity (timesheet) were done
        """
        return self.__activities_date

    @activities_date.setter
    def activities_date(self, value):
        if isinstance(value, datetime.datetime):
            self.__activities_date = value
            return self.__activities_date

        if isinstance(value, str):
            try:
                date = datetime.datetime.strptime(value, self.format)
                self.__activities_date = date
                return self.__activities_date

            except ValueError:
                raise ValueError(
                    f"Your date: '{value}' does not match the format required {self.format}. Please check it.")

    def read_csv(self):
        """Reads a csv file
        """
        assert (self.path.endswith('.csv')
                ), f'You have provide a csv file: {self.path}!'

        with open(self.path, 'r', encoding='utf-8-sig') as file:
            data = csv.reader(file, delimiter=',')
            vals = list()

            for n, row in enumerate(data):
                if not n:
                    keys = row
                else:
                    vals.append(row)

            self._create_data_dict(keys, vals)

    def _create_data_dict(self, keys: list, vals: list) -> dict:
        """Creates a dict containing columns and rows of a csv file
        """
        vals = list(zip(*vals))
        keys = list(map(self._lowercase_keys, keys))
        data = dict(zip(keys, vals))

        for key, val in data.items():
            data[key] = list(val)

        self.data = data

    @staticmethod
    def _lowercase_keys(key: str) -> str:
        """Turns into lowercase the keys of data dict
        """
        return key.lower().strip()

    def remove_keys(self):
        """Removes keys from data dict
        """
        keys_to_remove = list(map(self._lowercase_keys,
                                  self.keys_to_remove))

        for key in keys_to_remove:
            self.data.pop(key, None)

    def replace_project_for_id(self):
        """Replaces project's name for its id in odoo.
        """
        projects = list(map(self._lowercase_keys, self.data['project']))
        project_ids = list()

        for project in projects:
            id = self.project_ids[project]
            project_ids.append(f'project.project_project_{id}')

        self._update_dict_data('project', project_ids)

    def _update_dict_data(self, key: str, val: list):
        """Updates dict data with new values
        """
        self.data[key] = val

    def replace_duration_for_number(self):
        """Replaces time in string for numbers
        """
        durations = list(
            map(self._calculate_unit_amount, self.data['duration']))
        self._update_dict_data('duration', durations)

    @staticmethod
    def _calculate_unit_amount(duration: str) -> float:
        """Converts time in string to a number
        """
        format = "%H:%M:%S"
        convertion_factor = 1/3600
        duration = time.strptime(duration, format)
        unit_amount = datetime.timedelta(hours=duration.tm_hour,
                                         minutes=duration.tm_min,
                                         seconds=duration.tm_sec).total_seconds() * \
            convertion_factor
        return unit_amount

    def clean_descriptions(self):
        """This method removes the task id from activities' descriptions and saves it into a list
        """
        descriptions = list()
        self.task_ids = list()

        for description in self.data['description']:
            if self.sep in description:
                description = description.split(self.sep)
                self.task_ids.append(
                    f'project.project_task_{int(description[0])}')
                descriptions.append(description[1])

            else:
                self.task_ids.append(False)
                descriptions.append(description)

        self._update_dict_data('description', descriptions)

    def create_tasks(self):
        """Creates task_id column
        """
        self._update_dict_data('task_id/id', self.task_ids)

    def add_date(self):
        """Adds date column
        """
        dates = [self.activities_date.strftime(self.format)] *\
            len(self.data)
        self._update_dict_data('date', dates)

    def create_spreadsheet(self):
        """Creates a spreadsheet for uploading timesheet to Odoo
        """
        self.spreadsheet.data = self.data
        self.spreadsheet.columns_to_rename = self.columns_to_rename
        self.spreadsheet.create_workbook()

    def run(self):
        self.read_csv()
        self.remove_keys()
        self.replace_project_for_id()
        self.replace_duration_for_number()
        self.clean_descriptions()
        self.create_tasks()
        self.add_date()
        self.create_spreadsheet()

    def __call__(self) -> Any:
        self.run()
