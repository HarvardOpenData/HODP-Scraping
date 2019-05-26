from os import getcwd
from sys import executable
from crontab import CronTab

dirpath = getcwd()
cron = CronTab(tabfile='scrape.tab')

# Set environment variables here
cron.env['SHELL'] = '/bin/bash'

# Gets the path to the python executable running this script
# This assumes that this python binary covers all scraper's dependencies
python = executable

# Jobs to be run every 24hrs
cmd_daily = [
    (f'{python} {dirpath}/scrapers/gocrimson/scrape_gocrimson.py',
     'Scrape Gocrimson'),
    (f'{python} {dirpath}/scrapers/crime/scrape_crime.py', 'Scrape crime')
]

# Create jobs if they do not already exist
for command, description in cmd_daily:
    if list(cron.find_command(command)) == []:
        job = cron.new(command=command, comment=description)
        if job.is_valid():
            job.run()
            job.every().dom()
        else:
            job.delete()


cron.write()
