from sentence_transformers import SentenceTransformer
import pandas as pd
import os,chromadb,time
from clean import *
dirname='verified-claims';total=0
csv_dir='../data_dry/politifact/'+dirname+'/'
model = SentenceTransformer('WhereIsAI/UAE-Large-V1', device="cpu")
client = chromadb.PersistentClient(path=dirname+".db")
collection = client.get_or_create_collection(name='data', metadata={"hnsw:space": "l2"}) # or ip or cosine
for file in os.listdir(csv_dir):
    if file.endswith('.csv'):
        fn=file.split('.')[0]
        print(file)
        df = pd.read_csv(csv_dir+'/'+file, header=None, names=['blk','claim','date','verified_claim_url','true','speaker','verified_claim','article'])
        df['ids'] = df.reset_index().apply(lambda row: file + ',' +str(row['index']) , axis=1).tolist()# df['article'] = df['article'].fillna('') # df['docs'] = df.apply(lambda row: clean_text(row['article']), axis=1).tolist()
        df['speaker'] = df['speaker'].fillna('')
        df['docs'] = df.apply(lambda row: row['speaker'].lower()+' says '+clean_text(row['verified_claim'].replace('says','').strip())+' at '+row['date'], axis=1).tolist()
        df['urls'] = df.reset_index().apply(lambda row: row['verified_claim_url'].split('statements/')[1].rstrip('/') , axis=1).tolist()
        total=0;cnt=100;start=time.time()
        for i in range(0, df.shape[0], cnt):
            cf = df[i:i+cnt]
            embeddings = model.encode(cf['docs'].tolist()).tolist()
            collection.upsert(ids=[str(id) for id in cf['ids'].tolist()], embeddings=embeddings, metadatas=[{'url': url} for url in cf['urls'].tolist()])
            sofar=time.time()-start
            total+=cnt
            print(sofar,sofar/total,total)




