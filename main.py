from utils import parse_config
from timesheet_pipeline import TimesheetPipeline


if __name__ == '__main__':
    path = 'Toggl_Track_summary_report_2023-08-18_2023-08-18.csv'
    keys_to_remove = ['Client']
    keys_to_rename = {
        'Project': 'project_id/id',
        'Description': 'name',
        'Duration': 'unit_amount'
    }
    project_ids = {
        'laboral': 4
    }
    sep = '-'

    pipline = TimesheetPipeline(path,
                                keys_to_remove,
                                keys_to_rename,
                                project_ids,
                                sep)
    pipline.activities_date = '2023-08-25'
    pipline()
