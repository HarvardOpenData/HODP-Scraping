# Update virtualenv and install all scraper dependencies
pip3 install -r requirements.txt

for dir in scrapers/*; do
  pip3 install -r ${dir}/requirements.txt
done

pip3 install koala_cron/
pip3 freeze > requirements.txt
