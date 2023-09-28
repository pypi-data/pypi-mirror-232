from datetime import datetime, timedelta, date

from termcolor import colored
from prettytable import PrettyTable

from timetrack import utils
from timetrack.config import cfg
from timetrack.timeblock import TimeBlock

def make_report_table(df: utils.pd.DataFrame) -> str:
    """ 
    Makes a table of timeblock counts and total durations for each project.
    """
    # TODO: report should probably include progress on current timeblock
    unique_labels = df['label'].unique()
    label_durations = [df[df['label'] == label]['duration'].sum().total_seconds()
                       for label in unique_labels] 
    label_block_count = [len(df[df['label'] == label]) for label in unique_labels] 

    t = PrettyTable()
    t.add_column('Task', unique_labels)
    t.add_column('Blocks', label_block_count)
    t.add_column('Hours', [f"{d / 60.0 / 60.0:.1f}" for d in label_durations])
    t.add_column('% Hours', [f"{100.0 * d / sum(label_durations):.1f}" 
                             for d in label_durations])
    t.align = 'r'
    # t.add_row([bold('total'), bold(sum(label_block_count)), 
    # bold(seconds_to_hm(sum(label_durations))), '-'])

    return t

def create_report(
    df: utils.pd.DataFrame,
    x: list[str]
    ):
    """
    Creates and prints a report of timeblocks corresponding to the timeframe
    specified in the user command.
    """
        
    if len(x) == 1: # blank command prints daily report
        print_day_report(df)

    elif x[1].lower() in ['full', 'all']: # full report
        print_full_report(df)

    elif x[1].lower() in ['today', 'day', 'daily']: # today's report
        print_day_report(df)
    
    elif x[1].lower() in ['yesterday']:
        # TODO: implement yesterday report
        print("Yesterday report not yet implemented.")
        print_yesterday_report(df)
    
    elif x[1].lower() in ['week', 'weekly']:
        # TODO: implement weekly report
        print("Weekly report not yet implemented.")
        print_week_report(df)

    elif x[1].lower() in ['pp', 'payperiod']: # payperiod report
        print_pp_report(df)

def print_day_report(
        df: utils.pd.DataFrame
    ) -> None:

    midnight_today = datetime.today().replace(
        minute=0,
        hour=0,
        second=0,
        microsecond=0
    )
    today_blocks = df[df['t_start'] >= midnight_today]

    print(f"Summary for today {midnight_today.strftime('%m/%d/%Y')}:")
    t = make_report_table(today_blocks)
    print(t)

    today_logged_hours = (today_blocks['duration'].sum().total_seconds() 
                            / 60.0 / 60.0)
    today_goal = cfg['daily_hour_goal']
    # print('[' + '=' * 5 + '>' + ' ' * 10 + ']')

    # Incorporate active block into progress for today
    # active_hours = (active_blocks[0].get_elapsed_time() 
    #                 / 60.0 / 60.0 if active_blocks else 0)
    # today_total_hours = today_logged_hours + active_hours
    today_total_hours = today_logged_hours

    print(f"* You've worked {today_total_hours:0.1f} / {today_goal:0.1f}"
            f" hours ({100 * today_total_hours / today_goal:.1f}%) today.")

    today_hours_remaining = today_goal - today_total_hours
    if today_hours_remaining > 0.02: # ittle leeway at the end of the day :)
        predicted_finish = (datetime.now() + 
            timedelta(hours=today_hours_remaining)).strftime('%I:%M %p')
        
        print(colored(f"* You have {today_hours_remaining:.1f} "
                        f"hours left to work today.", 'yellow'))
        print(f"* You could meet your goal by {predicted_finish}.")
    else:
        print(colored(
            "* You've completed your hours for today! Great Job!",
            'green')
        )

def print_pp_report(
        df: utils.pd.DataFrame
    ) -> None: 

    curr_pp_start = utils.get_curr_pp_start()
    curr_pp_blocks = df[df['t_start'] >= curr_pp_start] 

    curr_pp_start_string = curr_pp_start.strftime('%m/%d/%Y') 
    curr_pp_end_string = (curr_pp_start + utils.pp_duration 
                            - timedelta(1)).strftime('%m/%d/%Y') 

    print(f"Summary for current payperiod "
            f"{utils.bold(utils.get_curr_pp_name())}:")
    print(f"({curr_pp_start_string} - {curr_pp_end_string})")
    t = make_report_table(curr_pp_blocks)
    print(t)

    curr_pp_hours = (curr_pp_blocks['duration'].sum().total_seconds() 
                        / 60.0 / 60.0)
    curr_pp_goal = cfg['pp_hour_goal']
    print(f"* You've worked {curr_pp_hours:0.1f} / {curr_pp_goal:0.1f} "
            f"hours ({100 * curr_pp_hours / curr_pp_goal:.1f}%) "
            f"this payperiod.")

    pp_hours_remaining = curr_pp_goal - curr_pp_hours
    if pp_hours_remaining > 0:
        print(f"* You have {pp_hours_remaining:.1f} "
                f"hours left to work this payperiod.")
    else:
        print(colored(
            "* You've completed your hours for the payperiod! Great Job!",
            'green')
        )

def print_week_report():
    return

def print_yesterday_report():
    return

def print_full_report(
        df: utils.pd.DataFrame,
) -> None:
    
    # TODO: display the range of dates that exist in log
    print("Summary of full log file:")
    t = make_report_table(df)

    print(t)
    print(f"* Total hours logged: "
            f"{df['duration'].sum().total_seconds() / 60.0 / 60.0:.1f}")