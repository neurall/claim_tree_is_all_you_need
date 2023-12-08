from sentence_transformers import SentenceTransformer
import pandas as pd
import os,chromadb
from clean import *
dirname='fact-checking';total=0
csv_dir='../data_dry/politifact/'+dirname+'/'
model = SentenceTransformer('WhereIsAI/UAE-Large-V1', device="cpu")
client = chromadb.PersistentClient(path=dirname+".db")#client.reset()
collection = client.get_or_create_collection(name='data', metadata={"hnsw:space": "l2"}) # or ip or cosine
for file in os.listdir(csv_dir):
    if file.endswith('.csv'):
        fn=file.split('.')[0]
        print(file)
        df = pd.read_csv(csv_dir+'/'+file)
        df['date'] = fn[9:].replace('_', ' ')+' '+fn[:4]+'/'+fn[4:6]+'/'+fn[6:8]
        df['ids'] = df.reset_index().apply(lambda row: file + ',' + str(row['line_number'])+ ',' +str(row['index']) , axis=1).tolist()
        df['speaker'] = df['speaker'].fillna('')
        df['docs'] = df.apply(lambda row: row['speaker'].lower()+' says '+clean_text(row['verified_claim'].replace('says','').strip())+' at '+row['date'], axis=1).tolist()
        df['urls'] = df.reset_index().apply(lambda row: row['verified_claim_url'].split('statements/')[1].rstrip('/') , axis=1).tolist()
        embeddings = model.encode(df['docs']).tolist()
        collection.upsert(ids=[str(id) for id in df['ids']], embeddings=embeddings, metadatas=[{'url': url} for url in df['urls'].tolist()])