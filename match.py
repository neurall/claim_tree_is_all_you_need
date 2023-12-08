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
    n_results=30,include=["metadatas",'distances']
)
ids=f['ids']
urlsf=[x['url'] for x in f['metadatas']]
txt=''
for i,id in enumerate(ids):
    txt+=id+'\n'+urlsf[i]+'\n'
    for j,g in enumerate(v['metadatas'][i]):
        txt+=g['url']+' '+str(v['distances'][i][j])+'\n'
with open('results.txt', 'w') as f:
    f.write(txt)