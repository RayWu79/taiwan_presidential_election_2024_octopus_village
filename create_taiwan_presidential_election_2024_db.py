import pandas as pd
import sqlite3
import os
import re

class CreateTaiwanPresidentialElection2024DB:
    def __init__(self):
        file_names = os.listdir("data")
        county_names = []
        for file_name in file_names:
            if ".xlsx" in file_name:
                file_name_split = re.split("\\(|\\)", file_name) ## \\( Escape, |:or
                county_names.append(file_name_split[1])
        self.county_names = county_names
        
    def tidy_county_df(self, county_name: str):
        file_path = f"data/總統-A05-4-候選人得票數一覽表-各投開票所({county_name}).xlsx"
        df = pd.read_excel(file_path, skiprows=[0, 3, 4]) # Read the excel and skip first, fourth, and fifth rows
        df = df.iloc[:, :6] # Select all rows and keep first six columns
        candidates_info = df.iloc[0, 3:].values.tolist() # Get candidate information from first row and after fouth columns
        # .tolist(): Return the array as an a.ndim-levels deep nested list of Python scalars.
        df.columns = ["town", "village", "polling_place"] + candidates_info
        df.loc[:, "town"] = df["town"].ffill()
        # .ffill() Example
        #      A    B   C    D
        # 0  NaN  2.0 NaN  0.0
        # 1  3.0  4.0 NaN  1.0
        # 2  NaN  NaN NaN  NaN
        # 3  NaN  3.0 NaN  4.0
        #          |
        #          V
        #      A    B   C    D
        # 0  NaN  2.0 NaN  0.0
        # 1  3.0  4.0 NaN  1.0
        # 2  3.0  4.0 NaN  1.0
        # 3  3.0  3.0 NaN  4.0
        df.loc[:, "town"] = df["town"].str.strip() # remove space character
        df = df.dropna()
        df["polling_place"] = df["polling_place"].astype(int)
        id_variables = ["town", "village", "polling_place"]
        # Unpivot a DataFrame from wide to long format, optionally leaving identifiers set
        melted_df = pd.melt(df, id_vars=id_variables, var_name="candidate_info", value_name="votes") 
        melted_df["county"] = county_name
        return melted_df

    def concat_county_df(self):
        counties_df = pd.DataFrame()
        for county_name in self.county_names:
            county_df = self.tidy_county_df(county_name)
            counties_df = pd.concat([counties_df, county_df])
        counties_df = counties_df.reset_index(drop=True)
        numbers, candidates = [], []
        for elem in counties_df["candidate_info"].str.split("\n"):
            # parts of a string that match a given regular expression pattern with a new substring
            number = re.sub("\\(|\\)", "", elem[0])
            numbers.append(int(number))
            candidate = elem[1] + "/" + elem[2]
            candidates.append(candidate)
        # Select the specific columns we want
        presidential_votes = counties_df.loc[:, ["county", "town", "village", "polling_place"]]
        presidential_votes["number"] = numbers
        presidential_votes["candidate"] = candidates
        presidential_votes["votes"] = counties_df["votes"].values
        return presidential_votes

    def create_db(self):
        presidential_votes = self.concat_county_df()
        polling_places_df = presidential_votes.groupby(["county", "town", "village", "polling_place"]).count().reset_index()
        polling_places_df = polling_places_df[["county", "town", "village", "polling_place"]]
        polling_places_df = polling_places_df.reset_index()
        polling_places_df["index"] = polling_places_df["index"] + 1
        polling_places_df = polling_places_df.rename(columns={"index":"id"})

        candidates_df = presidential_votes.groupby(["number", "candidate"]).count().reset_index()
        candidates_df = candidates_df[["number", "candidate"]]
        candidates_df = candidates_df.reset_index()
        candidates_df["index"] = candidates_df["index"] + 1
        candidates_df = candidates_df.rename(columns={"index":"id"})

        join_keys = ["county", "town", "village", "polling_place"]
        votes_df = pd.merge(presidential_votes, polling_places_df, left_on=join_keys, right_on=join_keys, how="left")
        # df1
        #     lkey value
        # 0   foo      1
        # 1   bar      2
        # 2   baz      3
        # 3   foo      5
        # df2
        #     rkey value
        # 0   foo      5
        # 1   bar      6
        # 2   baz      7
        # 3   foo      8
        #       |
        #       V
        # df1.merge(df2, left_on='lkey', right_on='rkey')
        # lkey  value_x rkey  value_y
        # 0  foo        1  foo        5
        # 1  foo        1  foo        8
        # 2  bar        2  bar        6
        # 3  baz        3  baz        7
        # 4  foo        5  foo        5
        # 5  foo        5  foo        8
        
        votes_df = votes_df[["id", "number", "votes"]]
        votes_df = votes_df.rename(columns={"id":"polling_place_id", "number":"candidate_id"})
        connection = sqlite3.connect("data/taiwan_presidential_election_2024.db")
        polling_places_df.to_sql("polling_places", con=connection, if_exists="replace", index=False)
        candidates_df.to_sql("candidates", con=connection, if_exists="replace", index=False)
        votes_df.to_sql("votes", con=connection, if_exists="replace", index=False)
        cur = connection.cursor()
        drop_view_sql = """DROP VIEW IF EXISTS votes_by_village;"""
        create_view_sql = """
        CREATE VIEW votes_by_village AS
        SELECT polling_places.county,
               polling_places.town,
               polling_places.village,
               candidates.number,
               candidates.candidate,
               SUM(votes.votes) AS sum_votes
          FROM votes
          LEFT JOIN polling_places
            ON votes.polling_place_id = polling_places.id
          LEFT JOIN candidates
            ON votes.candidate_id = candidates.id
         GROUP BY polling_places.county,
               polling_places.town,
               polling_places.village,
               candidates.id;
        """
        cur.execute(drop_view_sql)
        cur.execute(create_view_sql)
        connection.close()

create_taiwan_presidential_election_2024_db = CreateTaiwanPresidentialElection2024DB()
create_taiwan_presidential_election_2024_db.create_db()
