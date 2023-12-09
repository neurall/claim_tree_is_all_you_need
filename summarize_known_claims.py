# Author: Ladislav Nevery
# Date: 1.12.2023
# Copyright (c) 2023 Ladislav Nevery. All rights reserved.

# Importing necessary libraries
import pandas as pd
import os, chromadb, openai
from datetime import datetime
from clean import *  # Assuming this is a custom module for text cleaning

dirname = 'fact-checking'; total = 0
csv_dir = '../data_dry/politifact/' + dirname + '/'

df1 = pd.read_csv('../data_dry/politifact/verified-claims/facts_with_articles.csv',header=None, names=['blk', 'claim', 'date', 'verified_claim_url', 'true', 'speaker', 'verified_claim', 'article'] )
df2 = pd.read_csv('../data_dry/politifact/verified-claims/20191030_remaining_politifacts.csv',header=None, names=['blk', 'claim', 'date', 'verified_claim_url', 'true', 'speaker', 'verified_claim', 'article'] )
df2 = df1.append(df2)

# Iterating over each file in the specified directory
for file in os.listdir(csv_dir):
    if file.endswith('.csv'):
        fn = file.split('.')[0]
        print(file)
        dt = 0
        # Reading the main CSV file
        df = pd.read_csv(csv_dir + '/' + file )

        df3 = df2.merge(df, on='verified_claim_url', how='inner')

        df3['article']=df3['article'].apply(clean_text)
 
        # Iterating over rows in the dataframe
        for index, row in df.iterrows():
            to = int(row['line_number'])
            frm = max(0, (to - 1) - 10)
            usr = 'WHEN: ' + when + '\nWHERE: ' + where + '.\nDEBATE_EXCERPT:\n' + '\n'.join(debate[frm:to - 1])
            name = row['speaker']

            # Defining the prompt for OpenAI's model
            sys = 'Summarize expand and explain last sentence of this debate excerpt made by '+name+'.make  selfcontained and as short succint summary as possible. always start and present info in summary in this following exact order. where when who claimed what to who. always use info where it was in original form from article dont simplify to just debate word. Never mention debate excerpt. Never mention the last sentence or in what sentence . '

            # Generating summary using OpenAI's Chat Completion model
            response = openai.ChatCompletion.create(
                model= "gpt-3.5-turbo",
                temperature=0,
                messages=[
                    {"role": "system", "content": sys},
                    {"role": "user", "content": usr}
                ]
            )
            output = response.choices[0].message['content']
            of.at[index, 'summary'] = output 
            of.to_csv('summaries/' + file, index=False)
