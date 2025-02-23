# Introduction

The "Finding the Octopus Village" project analyzes voting data from Taiwan's 2024 - 16th Presidential and Vice Presidential Election, using data from the Central Election Commission's database. It calculates voting rates for more than 7,700 villages and neighborhoods across Taiwan and compares them with the national voting rate. The project challenges two questionable claims made by news media:

1. Given that population demographics change and elections vary in type, it is unreasonable to designate a specific village/neighborhood as a permanent bellwether district.

2. The definition of "voting rates being very close to the final result" is ambiguous and lacks precision.

We utilized `pandas` and `sqlite3` for database construction, `numpy` for concept validation, and `gradio` for the final product implementation.

# How to Reproduce

1. Install Miniconda
2. Create the environment using `environment.yml`:
```bash
conda env create -f environment.yml
```

3. Place the 22 spreadsheet files titled "Presidential-A05-4-Candidate Vote Count List-By Polling Station" from the `data/` directory into your project's `data/` directory

4. Activate the environment and create the database:
```bash
python create_taiwan_presidential_election_2024_db.py
```
This will generate `taiwan_presidential_election_2024.db` in the `data/` directory

5. Launch the application:
```bash
python app.py
```
Then visit http://127.0.0.1:7860 in your browser to view the final product.