from os import getcwd
from sys import executable
from fnmatch import fnmatch

from crontab import CronTab

dirpath = getcwd()
cron = CronTab(tabfile='scrape.tab')

# Set environment variables here
cron.env['SHELL'] = '/bin/bash'

# Gets the path to the python executable running this script
# This assumes that this python binary covers all scraper's dependencies
python = executable


class InvalidTimeError(Exception):
    pass


def create_job(cmd):
    def set_time(job):
        time = cmd['time']
        def get_x(time): return time.split(' ')[1]
        if fnmatch(time, 'everyday'):
            job.every().dom()
        elif fnmatch(time, 'every ? hours'):
            job.hour.every(get_x(time))
        elif fnmatch(time, 'every ? days'):
            job.day.every(get_x(time))
        else:
            job.setall(time)

    command = cmd['command']
    comment = cmd['comment']

    if list(cron.find_command(command)) == []:
        job = cron.new(command=command, comment=comment)
        if job.is_valid():
            set_time(job)
        else:
            job.delete()


""" 'commands' contains the list of jobs to be run
    Dict interface:
        @command: the command to be run
        @comment: info associated with it
        @time   : when it is to be executed
        
    All implemented time descriptors:
    'everyday', 'every X hours', 'every Y days'
    where X is between 0 - 23 and where is Y is any natural number

    You may also input normal cron time expressions like '* * * * *' for more control
"""

# Note that all times are in UTC. So, 12:00am UTC becomes 8:00pm EST.

commands = [
    {
        'command': f'{python} {dirpath}/scrapers/gocrimson/scrape_gocrimson.py',
        'comment': 'Scrape Gocrimson',
        'time': 'everyday',
    },
    {
        'command': f'{python} {dirpath}/scrapers/crime/scrape_crime.py',
        'comment': 'Scrape crime',
        'time': '45 3 * * *'  # everyday at 3:45am UTC (11:45pm EST)
    },
    {
        'command': f'{python} {dirpath}/scrapers/grill_waits/scrape_grill_waits.py',
        'comment': 'Scrape grill wait times',
        'time': "*/5 11-13 * * * *"
          # every 5 minutes between hours of 11am-3pm, 5pm-7pm
    },
    {
        'command': f'{dirpath}/pull_and_run.sh',
        'comment': 'Pull changes from remote and reset crontab',
        'time': '0 12 * * *'  # everyday at 12:00pm UTC
    }
]

# Create jobs from 'command' list
for command in commands:
    create_job(command)

cron.write()
