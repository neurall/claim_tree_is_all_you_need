from sentence_transformers import SentenceTransformer
import pandas as pd
import os,chromadb,time,openai
from datetime import datetime
from clean import *#n_ctx=1500,
print(openai.Model.list())
dirname='fact-checking';total=0
csv_dir='../data_dry/politifact/'+dirname+'/'
model = 0#SentenceTransformer('WhereIsAI/UAE-Large-V1', device="cpu")
client = chromadb.PersistentClient(path=dirname+".db")#client.reset()
collection = client.get_or_create_collection(name='data', metadata={"hnsw:space": "l2"}) # or ip or cosine
for file in os.listdir(csv_dir):
    if file.endswith('.csv'):
        print(file)
        df = pd.read_csv(csv_dir+'/'+file)
        ds = pd.read_csv('summaries/'+file)
        df['ids'] = df.reset_index().apply(lambda row: file + ',' + str(row['line_number'])+ ',' +str(row['index']) , axis=1).tolist()
        df['urls'] = df.reset_index().apply(lambda row: row['verified_claim_url'].split('statements/')[1].rstrip('/') , axis=1).tolist()
        embeddings = model.encode(ds['summary'].apply(clean_text)).tolist()
        collection.upsert(ids=[str(id) for id in df['ids']], embeddings=embeddings, metadatas=[{'url': url} for url in df['urls'].tolist()])