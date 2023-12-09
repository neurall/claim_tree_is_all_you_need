import pandas as pd
import os, chromadb

# Set the directory name for the database
dirname = "fact-checking.db"
total = 0

# Set the directory path for the CSV files
csv_dir = "../data_dry/politifact/" + dirname + "/"

# Initialize persistent clients for the fact-checking and verified claims databases
clientf = chromadb.PersistentClient(path="fact-checking.db")
clientv = chromadb.PersistentClient(path="verified-claims.db")

# Get collections from the clients
cf = clientf.get_collection(name="data")
cv = clientv.get_collection(name="verified-claims")

# Query embeddings and metadatas from the fact-checking collection
f = cf.get(include=["embeddings", "metadatas"])

# Query verified claims based on embeddings with specified parameters
v = cv.query(query_embeddings=f["embeddings"],
             n_results=100,
             include=["metadatas", "distances"])

# Extract IDs and URLs from the fact-checking collection
ids = f["ids"]
urlsf = [x["url"] for x in f["metadatas"]]

# Initialize an empty string for storing the result text
txt = ""

# Iterate over the IDs and URLs, and append corresponding verified claims information
for i, id in enumerate(ids):
    txt += id + "\nCorrect:\n" + urlsf[i] + "\nRanking:\n"
    rank = 1

    for j, g in enumerate(v["metadatas"][i]):
        txt += f"{rank:03d} {g['url']} distance: {round(v['distances'][i][j])}\n"
        rank += 1

    txt += "\n"

# Write the result text to a file
with open("results.txt", "w") as f:
    f.write(txt)
