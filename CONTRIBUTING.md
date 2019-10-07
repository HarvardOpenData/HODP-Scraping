# Contributing

**Refer to the workflow for adding your own scraper.**

## Prerequisites

- `git`
- Python 3.7
- virtualenv

## Workflow

1. Look through the existing scrapers to make sure your ideas haven't already been implemented. If they have, feel free to extend the existing scraper instead.
2. If you're starting afresh, clone the repository onto your computer and **open a new branch using**: `git checkout -b BRANCH-NAME-HERE`. Please choose a branch name that is short but descriptive of your scraper. **Do not push your changes directly onto the master branch unless given prior permission by the repo maintainers.**
3. `cd` into `scrapers/` and `mkdir` a new directory for your scraper. The name of this directory should preferably be the same as the name of the branch, though this isn't a strict requirement.
4. `cd` into your directory, create a Python 3.7 virtualenv via `virtualenv --python=python3 hodp`. For the sake of consistency and so that you do not accidently commit your Python binary, please use "hodp" as the name of your virtualenv.
5. When you're ready to work, activate the virtualenv (normally `source hodp/bin/activate`) and start working.
6. When you're done, push your branch to GH and make a pull request. Please include in a comment the command to run your scraper (from the root directory of the project) and how often it should be executed.

While we are not necessarily limited from running scrapers written in languages other than Python, it is generally recommended that you do so for the sake of consistency and easily reviewing code. Please consult the repo maintainers if you strongly desire to write your scraper in another language.

## Local Testing
Inside of your python file, make sure to include 
```
import sys
sys.append(".")
```
at the top so that you can use other packages.

In order to dev with firestore, there are two options.

If you **have credentials**, make sure that you have your credentials as `scraping_creds.json` in the root folder. Then, in order to test you should run your scraper with the following command:
```
LOCAL=TRUE python3 scrapers/your_scraper/your_scraper.py
```
If you **do not have credentials**, then to use an in-memory instance of firestore, you should use the following command,
```
MOCK_FIRESTORE=TRUE python3 scrapers/your_scraper/your_scraper.py
```

## Ideas for what to scrape

If you're looking for ideas about what to scrape, here are a few datasets that you could look into collecting.
- Harvard's annual financial reports
- Course enrollment data
- Annual concentration counts
- Annual tuiton rates
- "Most read" headlines from the Crimson
- Annual statistics of your choice from the [Common Data Sets](https://oir.harvard.edu/common-data-set)

Many of these datasets can be sourced from several pages, so choose wisely :).
