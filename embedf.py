# Author: Ladislav Nevery
# Date: 1.12.2023
# Copyright (c) 2023 Ladislav Nevery. All rights reserved.

# Importing necessary libraries and modules
from sentence_transformers import SentenceTransformer
import pandas as pd
import os, chromadb, time, openai
from datetime import datetime
from clean import *  # Importing cleaning utilities, assuming custom functions for text cleaning

# Printing available models from OpenAI, for informational purposes
print(openai.Model.list())

# Setup for processing files in a specific directory
dirname = 'fact-checking'
total = 0
csv_dir = '../data_dry/politifact/' + dirname + '/'

# Initializing the Sentence Transformer model with a specific pre-trained model
model = SentenceTransformer('WhereIsAI/UAE-Large-V1', device="cpu")

# Setting up a persistent database client for data storage and retrieval
client = chromadb.PersistentClient(path=dirname + ".db")  # client.reset() is commented out, could be used to reset the client

# Creating or retrieving a data collection with specific configuration
collection = client.get_or_create_collection(name='data', metadata={"hnsw:space": "l2"})  # Configuration for the HNSW algorithm space

# Processing each CSV file in the designated directory
for file in os.listdir(csv_dir):
    if file.endswith('.csv'):
        print(file)
        df = pd.read_csv(csv_dir + '/' + file)  # Reading the main data file
        ds = pd.read_csv('summaries/' + file)  # Reading associated summaries

        # Generating unique identifiers for each row in the dataframe
        df['ids'] = df.reset_index().apply(lambda row: file + ',' + str(row['line_number']) + ',' + str(row['index']), axis=1).tolist()
        
        # Extracting URLs from the verified_claim_url field
        df['urls'] = df.reset_index().apply(lambda row: row['verified_claim_url'].split('statements/')[1].rstrip('/'), axis=1).tolist()
        
        # Encoding summaries after cleaning the text, and converting them to a list
        embeddings = model.encode(ds['summary'].apply(clean_text)).tolist()

        # Upserting data into the collection with embeddings and metadata
        collection.upsert(ids=[str(id) for id in df['ids']], embeddings=embeddings, metadatas=[{'url': url} for url in df['urls'].tolist()])
