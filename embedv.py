# Author: Ladislav Nevery
# Date: 1.12.2023
# Copyright (c) 2023 Ladislav Nevery. All rights reserved.

# Importing necessary libraries
from sentence_transformers import SentenceTransformer
import pandas as pd
import os, chromadb, time
from clean import *  # Assuming this is a custom module for text cleaning

# Setup for directory and initial variables
total = 0
dirname = 'verified-claims'
csv_dir = '../data_dry/politifact/' + dirname + '/'

# Loading the Sentence Transformer model
model = SentenceTransformer('WhereIsAI/UAE-Large-V1', device="cpu")

# Setting up a database client and creating or retrieving a data collection
client = chromadb.PersistentClient(path=dirname + ".db")
collection = client.get_or_create_collection(name='data', metadata={"hnsw:space": "l2"})

# Processing each CSV file in the designated directory
for file in os.listdir(csv_dir):
    if file.endswith('.csv'):
        fn = file.split('.')[0]
        print(file)

        # Reading CSV file with specified column names
        df = pd.read_csv(csv_dir + '/' + file, header=None, names=['blk', 'claim', 'date', 'verified_claim_url', 'true', 'speaker', 'verified_claim', 'article'])

        # Generating unique identifiers for each row
        df['ids'] = df.reset_index().apply(lambda row: file + ',' + str(row['index']), axis=1).tolist()
        
        # Handling missing speaker values and creating a cleaned document column
        df['speaker'] = df['speaker'].fillna('')
        df['docs'] = df.apply(lambda row: row['speaker'].lower() + ' says ' + clean_text(row['verified_claim'].replace('says', '').strip()) + ' at ' + row['date'], axis=1).tolist()

        # Extracting URLs from the verified_claim_url field
        df['urls'] = df.reset_index().apply(lambda row: row['verified_claim_url'].split('statements/')[1].rstrip('/'), axis=1).tolist()

        # Initializing variables for performance measurement
        total = 0
        cnt = 100
        start = time.time()

        # Processing and encoding the data in batches
        for i in range(0, df.shape[0], cnt):
            cf = df[i:i + cnt]
            embeddings = model.encode(cf['docs'].tolist()).tolist()
            collection.upsert(ids=[str(id) for id in cf['ids'].tolist()], embeddings=embeddings, metadatas=[{'url': url} for url in cf['urls'].tolist()])
            
            # Performance tracking
            sofar = time.time() - start
            total += cnt
            print(sofar, sofar / total, total)
