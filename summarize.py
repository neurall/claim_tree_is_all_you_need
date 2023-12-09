import pandas as pd
import os,chromadb,openai
from datetime import datetime
from clean import *

dirname='fact-checking';total=0
csv_dir='../data_dry/politifact/'+dirname+'/'
for file in os.listdir(csv_dir):
    if file.endswith('.csv'):
        fn=file.split('.')[0]        
        print(file)
        dt=0
        df = pd.read_csv(csv_dir+'/'+file)
        try:
            dt = pd.read_csv(csv_dir.replace(dirname,'transcripts')+'/'+file.replace('.csv','.tsv'),sep='\t', index_col=False, header=None, names=['id','speaker','text','no'])
        except:
            print('error',file)
            continue
        sb=dt.drop(['id','no'],axis=1)
        of = df[['line_number']].copy()
        df = df.assign(summary='')
        df_list = sb.values.tolist()
        debate = [' '.join(map(str, row)) for row in df_list]
        date = datetime.strptime(fn.split('_',1)[0], '%Y%m%d')
        when = date.strftime('%B %d, %Y')
        day = int(date.strftime('%d'))
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        when = when.replace(date.strftime('%d'), str(day) + suffix)
        where=fn.split('_',1)[1].replace('_',' ')
        txt=debate
        for index, row in df.iterrows():
            to=int(row['line_number'])
            frm=max(0,(to-1)-10)
            usr = 'WHEN: '+when+'\nWHERE: '+where+'.\nDEBATE_EXCERPT:\n'
            usr+= '\n'.join(debate[frm:to-1])
            name=row['speaker']
            sys='Summarize claim in the last sentence of this debate excerpt made by '+name+'.dont mention sentence was last. The summary should be factually self-contained containin all minimum facts for factchecking later begin alwais with who claims to who where(event name +city + state if available) when(date with month in word form)  . Start the summary by specifying the topic under discussion and how '+name+' is claimed in this line, including details of '+name+'s counterarguments or supporting points if made before and needed for this line. make sure selfcontained sentence always contains where and when statement was made to who and why.'
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                temperature=0,
                messages=[
                    {"role": "system", "content": sys},
                    {"role": "user", "content": usr}
                ]
            )
            output= response.choices[0].message['content']   
            of.at[index, 'summary'] = output 
            of.to_csv('summaries/'+file, index=False)