import pandas as pd
import sqlite3
import numpy as np

connection = sqlite3.connect("data/taiwan_presidential_election_2024.db")
votes_by_village = pd.read_sql("""SELECT * FROM votes_by_village;""", con=connection)
connection.close()
total_votes = votes_by_village["sum_votes"].sum()
# print(votes_by_village.groupby("number")["sum_votes"].sum())
country_persentage = votes_by_village.groupby("number")["sum_votes"].sum() / total_votes
# print(country_persentage)
vector_a = country_persentage.values
# print(vector_a)
groupby_variables = ["county", "town", "village"]
village_total_votes = votes_by_village.groupby(groupby_variables)["sum_votes"].sum()
# print(village_total_votes)
merged = pd.merge(votes_by_village, village_total_votes, left_on=groupby_variables, right_on=groupby_variables, how="left")
merged["village_percentage"] = merged["sum_votes_x"] / merged["sum_votes_y"]
merged = merged[["county", "town", "village", "number", "village_percentage"]]
# print(merged)
# Return reshaped DataFrame organized by given index / column values.
pivot_df = merged.pivot(index=["county", "town", "village"], columns="number",
                        values="village_percentage").reset_index()
#     foo   bar  baz  zoo
# 0   one   A    1    x
# 1   one   B    2    y
# 2   one   C    3    z
# 3   two   A    4    q
# 4   two   B    5    w
# 5   two   C    6    t
#           |
#           V
# bar  A   B   C
# foo
# one  1   2   3
# two  4   5   6

pivot_df = pivot_df.rename_axis(None, axis=1) # axis=1 : column, axis=0: row
# print(pivot_df)

cosine_similarities = []
length_vector_a = pow((vector_a**2).sum(), 0.5) # The pow() function returns the value of x to the power of y (x^y).
for row in pivot_df.iterrows():
    vector_bi = np.array([row[1][1], row[1][2], row[1][3]])
    vector_a_dot_vector_bi = np.dot(vector_a, vector_bi) # Dot product of two arrays.
    length_vector_bi = pow((vector_bi**2).sum(), 0.5)
    cosine_similarity = vector_a_dot_vector_bi / (length_vector_a * length_vector_bi)
    cosine_similarities.append(cosine_similarity)
# print(len(cosine_similarities))

cosine_similarity_df = pivot_df.iloc[:, :]
cosine_similarity_df["cosine_similarity"] = cosine_similarities
cosine_similarity_df = cosine_similarity_df.sort_values(["cosine_similarity", "county", "town", "village"], ascending=[0, 1, 1, 1])
cosine_similarity_df = cosine_similarity_df.reset_index(drop=True).reset_index()
cosine_similarity_df["index"] = cosine_similarity_df["index"] + 1
column_names_to_revise = {
    "index": "similarity_rank",
    1: "candidates_1",
    2: "candidates_2",
    3: "cnadidates_3"
}
cosine_similarity_df = cosine_similarity_df.rename(columns=column_names_to_revise)
# print(cosine_similarity_df.head(10))
def filter_county_town_village(df, county_name: str, town_name: str, village_name: str):
    county_condition = df["county"] == county_name
    town_condition = df["town"] == town_name
    village_condition = df["village"] == village_name
    return df[county_condition & town_condition & village_condition]

print(filter_county_town_village(cosine_similarity_df, "臺北市", "士林區", "天玉里"))