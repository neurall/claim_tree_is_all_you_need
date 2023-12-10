# Author: Ladislav Nevery
# Date: 1.12.2023
# Copyright (c) 2023 Ladislav Nevery. All rights reserved.

# Importing necessary libraries
import pandas as pd
import os, openai,time
from datetime import datetime
from clean import *  # Assuming this is a custom module for text cleaning

dirname = 'fact-checking'; total = 0
csv_dir = '../data_dry/politifact/' + dirname + '/'

if not os.path.exists('summaries.emb'):
    os.makedirs('summaries.emb')

# Iterating over each file in the known claims directory
kf=[];sf=[];sn=[]; total=0; found=0; multi=0; baddates=0; missing=0
kdir='../data_dry/politifact/verified-claims/'
for file in os.listdir(kdir):
    if file.endswith('.csv'):
        df = pd.read_csv(kdir+'/'+file,header=None, names=['blk', 'claim', 'date', 'verified_claim_url', 'true', 'speaker', 'verified_claim', 'article'] )
        df['verified_claim_url']=df['verified_claim_url'].replace(to_replace=r'^(http://www\.|https://www\.|http://|https://)', value='', regex=True)
        kf.append(df)
        try:
            df1= pd.read_csv('summaries.emb/'+file)
        except:
            df1=df[['verified_claim']].rename(columns={'verified_claim': 'summary'})
            df1['ours']=0
        sf.append(df1)
        sn.append(file)

# Iterating over each file in the input claims directory
for file in os.listdir(csv_dir):
    if file.endswith('.csv'):
        fn = file.split('.')[0]
        print(file,'                                                                    ')

        # Reading the main input claims CSV file. Typically 10 rows.
        df = pd.read_csv(csv_dir + '/' + file )
        df['verified_claim_url']=df['verified_claim_url'].replace(to_replace=r'^(http://www\.|https://www\.|http://|https://)', value='', regex=True)

        # loop 10 or so input claims per csv debate file
        for i, row in df.iterrows():
            url = row['verified_claim_url']
            total+=1
            # loop over currently two big known claims csv files
            for j,k in enumerate(kf):
                tmp = k[k['verified_claim_url'] == url]  
                if not tmp.shape[0]:
                    baddates+=1
                    title=url.rstrip('/').split('/')[-1]
                    tmp = k[k['verified_claim_url'].str.contains(title)]
                if not tmp.shape[0]:
                    missing+=1
                # loop over rows in this one big known claims file with 16000 rows.
                for rowno, row2 in tmp.iterrows():
                    if sf[j].at[rowno, 'ours'] == 1:
                        continue
                    article=clean_text(row2['article'])
                    found+=1
                    date = datetime.strptime(fn.split('_', 1)[0], '%Y%m%d')
                    when = date.strftime('%B %d, %Y')
                    day = int(date.strftime('%d'))
                    suffix = "th" if 4 <= day <= 20 or 24 <= day <= 30 else ["st", "nd", "rd"][day % 10 - 1]
                    when = when.replace(date.strftime('%d'), str(day) + suffix)

                    # mark multi
                    if tmp.shape[0]>1:
                        multi+=1

                    where = fn.split('_', 1)[1].replace('_', ' ')
                    usr = 'WHEN: ' + when + '\nWHERE: ' + where + '.\nDEBATE_EXCERPT:\n' 
                    name = row['speaker']

                    # Defining the prompt for OpenAI's model
                    sys = 'Summarize expand and explain a claim made by '+name+'. make  selfcontained and as short succint summary as possible. always start and present info in summary in this following exact order. where when who claimed what to who. always use info where it was in original form from article dont simplify to just debate word. Never mention debate excerpt. Never mention the last sentence or in what sentence . '

                    # Generating summary using OpenAI's Chat Completion model
                    response=0
                    while 1:
                        try:
                            response = openai.ChatCompletion.create(
                                model= "gpt-3.5-turbo",
                                temperature=0,
                                messages=[
                                    {"role": "system", "content": sys},
                                    {"role": "user", "content": usr+article}
                                ]
                            )
                            break
                        except:
                            time.sleep(10)
                
                    output = response.choices[0].message['content']

                    sf[j].at[rowno, 'summary'] = output 
                    sf[j].at[rowno, 'ours'] = 1
                    sf[j].to_csv('summaries.emb/'+sn[j], index=False)

                    print('total',total,'found',found,'datesoff',baddates,'missing',missing,'multi',multi,end='\r')

      