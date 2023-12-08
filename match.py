import pandas as pd
import os,chromadb
dirname="fact-checking.db";total=0
csv_dir='../data_dry/politifact/'+dirname+'/'
clientf = chromadb.PersistentClient(path="fact-checking.db")#client.reset()
clientv = chromadb.PersistentClient(path="verified-claims.db")#client.reset()
cf = clientf.get_collection(name='data')
cv = clientv.get_collection(name='verified-claims')
f=cf.get(include= ['embeddings','metadatas'])
v=cv.query(
    query_embeddings=f['embeddings'],
    n_results=10,include=["metadatas"]
)
ids=f['ids']
urlsf=[x['url'] for x in f['metadatas']]
urlsv=[x[0]['url'] for x in v['metadatas']]
txt=''
for i,id in enumerate(ids):
    txt+=id+'\n'+urlsf[i]+'\n'+urlsv[i]+'\n'
with open('results.txt', 'w') as f:
    f.write(txt)