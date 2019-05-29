# Harvard Open Data Project Scrapers

A basic repo for all of the automated HODP scraping scripts

## Contributing

Please refer to `CONTRIBUTING.md` for instructions on how to add your own scraper.

## Deploying

1. If you have access, ssh into the instance, and run `sudo su` to login again as the root user.
2. Navigate to the project and run

```bash
source hopd/bin/activate
./resolve_reqs
./init_crontab
crontab scrape.tab
```

## TODOs

- Add logging system
- Add unit tests

## Changelog

- **05/25/19 #2 (kevalii)**
  - Reverted the routing referenced in #1
  - Added `init_crontab.sh`, `write_cron.py`, and `resolve_reqs.py`.
    - `write_cron.py` writes cron jobs to a crontab (`scrape.tab`) using an API provided by [python-crontab](https://pypi.org/project/python-crontab/) package. You can still write cron jobs directly into `scrape.tab`; this just provides a perhaps more organized way of writing cron jobs in.
      - _NOTE: `scrape.tab` isn't provided in the repo. Either `touch` it locally or execute `init_crontab.sh`_
    - `init_crontab.sh` executes `write_cron.py` but it does not set the crontab. Make any changes to `scrape.tab` and then execute `crontab scrape.tab`.
    - `resolve_reqs.py` goes through all the `requirements.txt`s in each subdirectory of `scrapers/` and installs the dependencies, updating the root directory's `requirements.txt` as well.
  - `scrapers/crime/scrape_crime.py` no longer features the scrape function referenced in #1.
- **05/25/19 #1 (kevalii)**
  - Set up routing, enabling us to add more scrapers (and schedule them) in a sustainable manner.
  - Added `gocrimson` scraper at `/scrape/gocrimson` and a corresponding cron job.
    - While the scraper has also been added to this repo, it is actually executed by an GCloud function that uses a local copy of the source code for the scraper. For the future, we'll have to adjust this so that the function is sourced from this repo instead.
  - Modified `crime` scraper to route to `/scrape/crime`.
    - Wrapped relevant code in a `scrape` function in the renamed src file `scrape_crime.py` so that the scraper is executed by a call to `scrape` instead of just running at the top-level.
  - Moved to each scraper to a respective folder in `scrapers/` that also contains each scraper's respective dependencies in a `requirements.txt`.
