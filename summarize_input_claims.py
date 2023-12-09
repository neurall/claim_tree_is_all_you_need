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

# Iterating over each file in the specified directory
for file in os.listdir(csv_dir):
    if file.endswith('.csv'):
        fn = file.split('.')[0]        
        print(file)
        dt = 0

        # Reading the main CSV file
        df = pd.read_csv(csv_dir + '/' + file)

        # Trying to read a transcript file; if not found, skip to the next file
        try:
            dt = pd.read_csv(csv_dir.replace(dirname, 'transcripts') + '/' + file.replace('.csv', '.tsv'), sep='\t', index_col=False, header=None, names=['id', 'speaker', 'text', 'no'])
        except:
            print('error', file)
            continue
        if os.path.isfile('summaries.emb/' + file):
            continue
        # Preparing the data for summary generation
        sb = dt.drop(['id', 'no'], axis=1)
        of = df[['line_number']].copy()
        df = df.assign(summary='')
        df_list = sb.values.tolist()
        debate = [' '.join(map(str, row)) for row in df_list]

        # Formatting the date
        date = datetime.strptime(fn.split('_', 1)[0], '%Y%m%d')
        when = date.strftime('%B %d, %Y')
        day = int(date.strftime('%d'))
        suffix = "th" if 4 <= day <= 20 or 24 <= day <= 30 else ["st", "nd", "rd"][day % 10 - 1]
        when = when.replace(date.strftime('%d'), str(day) + suffix)

        where = fn.split('_', 1)[1].replace('_', ' ')
        txt = debate

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
