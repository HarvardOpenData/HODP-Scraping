# Update virtualenv and install all scraper dependencies
pip install -r requirements.txt

for dir in scrapers/*; do
  pip install -r ${dir}/requirements.txt
done

pip freeze > requirements.txt