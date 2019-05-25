# Harvard Open Data Project Scrapers
A basic repo for all of the automated HODP scraping scripts

##
Changelog

- 05/25/19 (kevalii)
  - Set up routing, enabling us to add more scrapers (and schedule them) in a sustainable manner.
  - Added `gocrimson` scraper at `/scrape/gocrimson`. 
    - While the scraper has also been added to this repo, it is actually executed by an GCloud function that uses a local copy of the source code for the scraper. For the future, we'll have to adjust this so that the function is sourced from this repo instead.
  - Modified `crime` scraper to route to `/scrape/crime`. 
    - Wrapped relevant code in a `scrape` function in the renamed src file `scrape_crime.py` so that the scraper is executed by a call to `scrape` instead of just running at the top-level.
  - Moved to each scraper to a respective folder in `scrapers/` that also contains each scraper's respective dependencies in a `requirements.txt`.