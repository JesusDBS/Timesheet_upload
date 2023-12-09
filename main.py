from utils import parse_config, update_date_in_filename
from timesheet_pipeline import TimesheetPipeline


def main():
    """Main script's function
    """
    data = parse_config(path='config.json')
    date = data['date'] or False

    path = update_date_in_filename(path=data['path'], date=date)

    pipline = TimesheetPipeline(path=path,
                                keys_to_remove=data['keys_to_remove'],
                                columns_to_rename=data['columns_to_rename'],
                                project_ids=data["project_ids"],
                                sep=data['sep']
                                )
    
    if date:
        pipline.set_activities_date(date)

    pipline()


if __name__ == '__main__':
    main()
