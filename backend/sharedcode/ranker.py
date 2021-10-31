import metapy
import pytoml
import json
import tempfile
import os
import uuid
import math
import logging
import azure.functions as func

class PassageRanker:

    def __init__(self,query,passages,context):
        self.query = query
        self.passages = passages
        self.context = context
        self.tmppath = ""
        self.corpuspath = ""
        self.configpath = ""
        self.id = str(uuid.uuid4())

    def createcorpusandconfig (self):
        tmpdir = tempfile.gettempdir()
        #replace backslashes with forward
        tmpdir = tmpdir.replace("\\", "/")

        self.tmppath = tmpdir + "/passage" + self.id
        os.mkdir(self.tmppath)
        os.mkdir(self.tmppath + "/passage")

        #make line.toml
        lpath = self.tmppath + "/passage/line.toml"
        lfile = open(lpath,"w")
        lfile.write("type = \"line-corpus\"")
        lfile.write("\n")
        lfile.close()
        del lfile

        #make corpus
        self.corpuspath = self.tmppath + "/passage/passage.dat"
        cfile = open(self.corpuspath,"w")
        for passage in self.passages:
            passageid = passage["id"]
            passagetext = passage["passage"]
            cfile.write(passagetext)
            cfile.write("\n")
        cfile.close()
        del cfile

        #make config
        self.configpath = self.tmppath + "/config.toml"
        cfgfile = open(self.configpath, "w")
        cfgfile.write("stop-words = \"sharedcode/stopwords.txt\"")
        cfgfile.write("\n")
        cfgfile.write("prefix = \"" + self.tmppath+"\"")
        cfgfile.write("\n")        
        cfgfile.write("dataset = \"passage\"")
        cfgfile.write("\n")
        cfgfile.write("corpus = \"line.toml\"")
        cfgfile.write("\n")
        cfgfile.write("index = \"" +self.tmppath+"/idx\"")
        cfgfile.write("\n")
        cfgfile.write("[[analyzers]]")
        cfgfile.write("\n")
        cfgfile.write("method = \"ngram-word\"")
        cfgfile.write("\n")
        cfgfile.write("ngram = 1")
        cfgfile.write("\n")
        cfgfile.write("filter = \"default-unigram-chain\"")
        cfgfile.write("\n")
        cfgfile.close()
        del cfgfile

        return self.configpath

    def cleanup(self,dir):

        files = os.listdir(dir)
        for file in files:
            if file == '.' or file == '..': continue
            path = dir + os.sep + file
            if os.path.isdir(path):
                self.cleanup(path)
            else:
                os.unlink(path)
        os.rmdir(dir)

    def load_ranker(self):
        k1 = 1.2
        b = 0.75
        k3 = 500
        return metapy.index.OkapiBM25(k1, b, k3)
        #return metapy.index.DirichletPrior()

    def process(self):
        top_k = 10
        passagelist = list()
        
        logging.info("Building Index")
        configfile = self.createcorpusandconfig()
        idx = metapy.index.make_inverted_index(configfile)
        num_docs = idx.num_docs()

        if top_k > num_docs:
            top_k = num_docs

        ranker = self.load_ranker()
        query = metapy.index.Document()

        #some kind of threading issue here
        #hangs when there are results
        # not working: query.content("search text")
        # working: query.content("nothing")
        query.content(self.query.strip())
        #query.content("passage")
        #query.content("no values")

        logging.info('Starting ranking')
        try:
            results = ranker.score(idx, query, top_k)
        except:
            logging.info('Could not rank results')

        #cleanup
        logging.info('Cleaning up')
        del idx
        try:
            self.cleanup(self.tmppath)
        except:
            logging.info('Could not clean up')

        #Here is an example of 2 results: [(1, 0.22911424934864044), (0, 0.15130186080932617)]

        for result in results:
            rank = float(result[1])
            passageid = self.passages[result[0]]["id"]
            passagetext = self.passages[result[0]]["passage"]
  
            passagedict = dict()
            passagedict["id"] = passageid
            passagedict["rank"]=rank
            passagedict["passage"]=passagetext
            passagelist.append(passagedict)
                
        return json.dumps(passagelist)

