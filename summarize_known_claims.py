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

# Iterating over each file in the known claims directory
kf=[];sf=[];sn=[]
kdir='../data_dry/politifact/verified-claims/'
for file in os.listdir(kdir):
    if file.endswith('.csv'):
        df = pd.read_csv(kdir+'/'+file,header=None, names=['blk', 'claim', 'date', 'verified_claim_url', 'true', 'speaker', 'verified_claim', 'article'] )
        df['verified_claim_url'].replace(to_replace=r'^(http://www\.|https://www\.|http://|https://)', value='', regex=True)
        kf.append(df)
        sf.append(pd.DataFrame(columns=['summary']))
        sn.append(kdir+'/'+file)

# Iterating over each file in the input claims directory
for file in os.listdir(csv_dir):
    if file.endswith('.csv'):
        fn = file.split('.')[0]
        print(file)

        # Reading the main input claims CSV file. Typically 10 rows.
        df = pd.read_csv(csv_dir + '/' + file )
        df['verified_claim_url'].replace(to_replace=r'^(http://www\.|https://www\.|http://|https://)', value='', regex=True)

        # loop 10 or so input claims per csv debate file
        for i, row in df.iterrows():
            url = row['verified_claim_url']

            # loop over currently two big known claims csv files
            for j,k in enumerate(kf):
                tmp = k[k['verified_claim_url'] == url]
                tmp['article']=tmp['article'].apply(clean_text)
                
                # loop over rows in this one big known claims file with 16000 rows.
                # matching input claim url. And typically finding more than 1.
                for m, row2 in tmp.iterrows():
                    article=row2['article']
                    
                    date = datetime.strptime(fn.split('_', 1)[0], '%Y%m%d')
                    when = date.strftime('%B %d, %Y')
                    day = int(date.strftime('%d'))
                    suffix = "th" if 4 <= day <= 20 or 24 <= day <= 30 else ["st", "nd", "rd"][day % 10 - 1]
                    when = when.replace(date.strftime('%d'), str(day) + suffix)

                    where = fn.split('_', 1)[1].replace('_', ' ')
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
                    of = df[['line_number']].copy()
                    index=0
                    sf.at[index, 'summary'] = output 
                    sf.to_csv(sn[m], index=False)

      