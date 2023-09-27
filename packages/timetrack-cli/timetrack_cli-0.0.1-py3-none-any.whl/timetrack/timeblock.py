
import os
import csv
import pandas as pd
from datetime import datetime, timedelta, date
from dataclasses import dataclass, fields, asdict

from termcolor import colored

from timetrack import utils

@dataclass
class TimeBlock:
    label: str
    sublabel: str = None
    t_start: int = None
    t_end: int = None

    def begin(self, fixed_duration: float = None):
        self.t_start = datetime.now().isoformat()
        utils.start_block_printout(self)
        self.has_timer=False
        
    def save(self):
        """
        Save current progress on this block
        """
        # TODO: implement non-terminal saving behavior
        # We need a way to identify which entry in the log corresponds with the
        # current active timeblock. Ideally this is just the last one, but there
        # may be weird cases where it is not (multiple instances?). Perhaps we can 
        # check for timeblock equality based on label and start time

        return

    def done(self, log_path):
        self.t_end = datetime.now().isoformat()
        utils.end_block_printout(self)
        self.write_to_log(log_path)
    
    def write_to_log(self, log_path):
        """
        Write the current timeblock to a log file
        """
        # Make the log directory if it doesn't already exist
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        # TODO: we should also be checking if there is a header present in the
        # log file to enable 'a+'. Can use csv.Sniffer.has_header() for this
        mode = 'w+' if not os.path.exists(log_path) else 'a+'
        with open(log_path, mode) as f:
            writer = csv.DictWriter(
                f, fieldnames=[field.name for field in fields(self)]
            )
            if mode == 'w+':
                print("Starting a new log file at:", log_path)
                writer.writeheader()
            writer.writerow(asdict(self))
    
    def record_active_block(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Record the current active block into a given DataFrame
        """
        data_to_append = pd.DataFrame([asdict(self)])
        df = pd.concat([df, data_to_append], ignore_index=True)
        df['t_start'] = pd.to_datetime(df['t_start'])

        return df
    
    def get_elapsed_time(self):
        if self.t_end is None:
            elapsed_time = (datetime.now() - 
                            datetime.fromisoformat(self.t_start)).total_seconds()
        else:
            elapsed_time = (datetime.fromisoformat(self.t_end) - 
                            datetime.fromisoformat(self.t_start)).total_seconds()
        return elapsed_time 
 