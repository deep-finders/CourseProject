import metapy
import pytoml
import json
import tempfile
import os
import uuid
import math
from threading import Thread, Lock
import time

if __name__ == '__main__':

        configfile = "C:/Users/chkabat/AppData/Local/Temp/passagead419c44-2320-40c0-b15a-adfd57bbb3d4/config.toml"

        idx = metapy.index.make_inverted_index(configfile)
        num_docs = idx.num_docs()
        
        top_k = 1
        k1 = 1.2
        b = 0.75
        k3 = 500
        ranker =  metapy.index.OkapiBM25(k1, b, k3)
        query = metapy.index.Document()
        query.content("search text")

        #some kind of threading issue here
        results = ranker.score(idx, query, top_k)
        print(results)
