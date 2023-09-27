#!/usr/bin/env python

import sys
import os
from datetime import datetime, timedelta, date

import pandas as pd
from art import tprint
from termcolor import colored

from timetrack.timeblock import TimeBlock
from timetrack.reports import create_report
from timetrack.config import cfg
from timetrack import utils

def signal_handler(sig=None, frame=None):
    if active_blocks:
        active_blocks[0].done(log_path=log_path)
    print(f"\nGoodbye {cfg['user_name']}!")
    sys.exit(0)

def end_curr_block(active_blocks, ding=False):
    block = active_blocks[0]
    block.done(log_path=log_path)
    active_blocks.remove(block) # TODO: is this proper?

    if ding:
        utils.play_ding()

def process_command(cmd: str, active_blocks: list):
    x = cmd.split()
    try:
        cmd_name = x[0]
    except IndexError: # blank command
        return 
    
    if cmd_name == 'begin':
        if not active_blocks:
            try:
                label, sublabel = utils.parse_labels(x[1])
                block = TimeBlock(label=label, sublabel=sublabel)
            except IndexError:
                print("Specify a task name to begin a timeblock.")
                return
            
            try:
                if x[2] == 'for': # TODO: have this handle units
                    duration = x[3] # expects minutes currently
                    utils.set_timer(
                        float(duration),
                        target_func=end_curr_block,
                        args=[active_blocks, True]
                    )
                elif x[2] == 'until':
                    duration = x[3]
                    print("Absolute timer not implement yet.")
            except IndexError:
                pass

            block.begin()
            active_blocks.append(block)
        else:
            print(colored("A timeblock is already in progress. "
                          "End before starting a new one.", 'red')
            )
    
    elif cmd_name == 'end':
        if active_blocks:
            end_curr_block(active_blocks)
        else:
            print("No timeblock is currently active.")

    elif cmd_name == 'status':
        if active_blocks:
            utils.status_printout(active_blocks[0])
        else:
            print("No timeblock is currently active.")

    elif cmd_name == 'log':
        # TODO: logic for post-hoc time logging goes here
        print("Post-hoc logging not yet implemented.")

    elif cmd_name == 'report':
        df = utils.load_log(log_path) # load the log file into a dataframe
        if df is None:
            return
        if active_blocks:
            df = active_blocks[0].record_active_block(df) # add current block 

        create_report(df, x)
        
    elif cmd_name == 'reset':
        utils.clear_log(log_path)

    elif cmd_name == 'exit':
        signal_handler()
    
    else:
        print(colored(f"That's an invalid command. Please try again.", 'red'))

    single_block_err_msg = "Only a single active block is currently supported." 
    assert len(active_blocks) <= 1, single_block_err_msg
    return

if __name__ == "__main__":
    utils.configure_signal_handlers(signal_handler)

    global log_path
    log_path = utils.get_log_path()

    tprint("TimeTrack")
    print("Welcome to TimeTrack! Type a command to get started.")

    active_blocks = []
    while True:
        cmd = input('>> ')
        process_command(cmd, active_blocks) 

