import metapy
import pytoml
import json

class PassageRanker:

    def __init__(self,query,passages):
        self.query = query
        self.passages = passages

    def process(self):

        count = 1

        passagelist=list()

        for passage in self.passages:
            passageid = passage["id"]
            passagerank = count
            count = count+1
            passagedict = dict()
            passagedict["id"] = passageid
            passagedict["rank"]=passagerank
            passagelist.append(passagedict)

        #need to return passage ids and ranks
        return json.dumps(passagelist)

