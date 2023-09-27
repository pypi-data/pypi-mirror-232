
import sys
import os
import signal
import threading
import yaml
from copy import copy
from datetime import datetime, timedelta, date

import pandas as pd
from playsound import playsound
from termcolor import colored

from timetrack.config import cfg

PP_ANCHOR = datetime.fromisoformat('2022-11-06 23:59:59.999999')
pp_duration = timedelta(days=14)

# File-related functions
def get_log_path() -> str:
    """
    Determines the log file path using environment variable, or uses
    the default path if no environment variable is set.
    """

    DEFAULT_LOG_PATH = os.path.join(
        os.path.expanduser('~'),
        '.timetrack/',
        'log.csv'
    )
    log_path = os.environ.get('TIMETRACK_LOG_PATH', DEFAULT_LOG_PATH) 

    return os.path.expanduser(log_path)

def load_log(log_path: str) -> pd.DataFrame:
    # Load the log file into a dataframe
    try:
        df = pd.read_csv(log_path)
    except FileNotFoundError:
        print(colored(f"No log file '{log_path}' found.", 'red'))
        return

    # Compute all timeblock durations as a new dataframe column
    try:
        df['t_start'] = pd.to_datetime(df['t_start'])
        df['t_end'] = pd.to_datetime(df['t_end'])
        df['duration'] = df['t_end'] - df['t_start']
    except KeyError: 
        print(colored("Invalid log file format detected.", 'red'))
    
    return df

def clear_log(log_path: str):
    """
    Deletes the log file if it exists.
    """
    resp = input("Are you sure you want to reset your log file? (y/n): ")
    if resp.lower() in ['y', 'yes']:
        if os.path.exists(log_path):
            os.remove(log_path)
            print("Log file deleted.")
        else:
            print("No log file found for deletion.")
    else:
        print("Reset aborted.")

def configure_signal_handlers(signal_handler):
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGABRT, signal_handler)

# Timer-related functions
def set_timer(duration, target_func, args=None):
    """Sets a timer that calls a function after a certain amount of time"""

    end_time = datetime.now() + timedelta(minutes=duration)
    end_time_str = end_time.strftime('%I:%M %p')
    print(f"Setting a timer for {duration} minutes, until {end_time_str}")
    threading.Timer(60 * duration, target_func, args if args else []).start()

def play_ding(filepath="sounds/ding3.mp3"):
    playsound(filepath)

def str_to_datetime(s: str) -> datetime:
    """
    Takes in a string representation of a time (e.g., '10:30am', '6pm', etc.)
    and returns a datetime object representing that time today. If the time
    represented by the string has already passed today, the function returns
    a datetime object representing that time tomorrow.
    """
    return

# Time-related functions
def datetime_str():
    return datetime.now().strftime('(%I:%M %p, %D)')

def get_curr_pp_start():
    """
    Determine the start time of the current payperiod.
    """
    today = datetime.today()
    
    # increment anchor until it is in the future 
    pp_endpoint = copy(PP_ANCHOR)
    while (pp_endpoint + pp_duration) < today:
        pp_endpoint += pp_duration
    
    # increment by 1us to get Monday start to payperiod 
    curr_pp_start = pp_endpoint + timedelta(microseconds=1)

    return curr_pp_start

def get_curr_pp_name():
     # TODO: implement APL-style payperiod naming (e.g. 2022B24)
    
    # Get today's date
    today = date.today()

    # Get the year and the start date of the year
    year = today.year
    year_start = date(year, 1, 1)

    # Calculate the number of days between today and the start of the year
    delta = (today - year_start).days

    # Calculate the payperiod index
    pp_idx = delta // 14 + 1
    
    pp_name = f"{year}B{str(pp_idx).zfill(2)}"
    return pp_name

def seconds_to_hm(seconds):
    elapsed_mins = int(seconds // 60)

    if elapsed_mins >= 60:
        elapsed_hours = elapsed_mins // 60
        elapsed_mins = elapsed_mins - elapsed_hours * 60
        hours_text = f"{elapsed_hours} h "
    else:
        hours_text = ""
    mins_text = f"{elapsed_mins} m"

    return f"{hours_text}{mins_text}" 

# Text functions
def parse_labels(label_str: str) -> tuple:
    if ':' in label_str:
        label_sublabel = label_str.split(':')
        label = label_sublabel[0]
        sublabel = label_sublabel[1]
    else:
        label = label_str
        sublabel = ''
    
    return label, sublabel

# Display-related functions
def formatted_block_name(block):
    return colored(block.label, 'blue', attrs=['bold'])

def formatted_elapsed_time(block):
    elapsed_hm = seconds_to_hm(block.get_elapsed_time())
    return colored(elapsed_hm, attrs=['bold'])

def start_block_printout(block):
    print(colored('-' * 30 + " BEGIN " + '-' * 30, 'white'))
    print(f"{datetime_str()} Starting a timeblock for "
            f"{formatted_block_name(block)}. Good Luck!")
    
def status_printout(block):
    print(f"You've been working on {formatted_block_name(block)} " 
            f"for {formatted_elapsed_time(block)}")
    # TODO: have this additionally display progress for the day 
    # (time remaining, end time, etc.)
    
def end_block_printout(block):
    print(f"{datetime_str()} "
            f"Ending a timeblock for {formatted_elapsed_time(block)}")
    print(colored('-' * 31 + " END " + '-' * 31, 'white'))
    print(f"You completed a {formatted_elapsed_time(block)} block of "
          f"{formatted_block_name(block)}. Great Job!")

def bold(x):
    return colored(str(x), attrs=['bold'])