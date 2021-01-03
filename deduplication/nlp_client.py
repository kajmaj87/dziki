import http.client
import json
import argparse
from glob import glob
from rich.console import Console
from rich.traceback import install

install(show_locals=True)

console = Console()

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("-l", "--limit", type=int, default=5000, help="Limit amount of texts sent to server")
parser.add_argument("-s", "--show", type=int, default=200, help="Max amount of records to show")
parser.add_argument("-g", "--groups", type=str, default=[], help="Provide group names for grouping similar texts", nargs="+")
config = parser.parse_args()

def loadDocuments():
    docs, data = [], []
    for f in glob("data/*.json"):
        with open(f, "r", encoding="utf8") as json_file:
            data.extend(json.load(json_file)["results"])
    for d in data:
        docs.append(
            {
                "id": d["id"],
                "text": d["text"],
                "comment": d["comment"],
                "dup": d["is_duplicate"],
                "verdict": d["current_verdict"],
            }
        )
    return docs


def calculateScore(document):
    sim = document["similarities"]
    textScore = sim["text"] if "text" in sim else 0
    commentScore = sim["comment"] if "comment" in sim else 0
    return textScore ** 2 + commentScore ** 2

def createGroups(similarities, groupBy, groupThreshold=1):
    groups = []
    def findGroupWithContainingAnyId(groups, id1, id2):
        for g in groups:
            if id1 in g or id2 in g:
                return g
        return None
    def addDocumentsToGroup(groups, doc1, doc2):
        group = findGroupWithContainingAnyId(groups, doc1["id"], doc2["id"])
        def internalAdd(group, doc1, doc2):
            cdoc1 = dict(doc1)
            del cdoc1["id"]
            cdoc2 = dict(doc2)
            del cdoc2["id"]
            group[doc1["id"]] = cdoc1
            group[doc2["id"]] = cdoc2

        if group is None:
            group = {}
            internalAdd(group, doc1, doc2)
            groups.append(group)
        else:
            internalAdd(group, doc1, doc2)

    for s in similarities:
        if groupBy in s["similarities"] and s["similarities"][groupBy] >= groupThreshold:
            addDocumentsToGroup(groups, s["docs"][0], s["docs"][1])
    return groups



c = http.client.HTTPConnection("localhost", 8080)
d = {
    "documents": loadDocuments()[:config.limit],
    "fields": [
        {"name": "text", "min_similarity": 0.9, "min_length": 10, "boost_exact_match": True, "stop_word_removal": True},
        {"name": "comment", "min_similarity": 0.9, "min_length": 10},
    ],
}
c.request("POST", "/process", json.dumps(d))
doc = json.loads(c.getresponse().read())
similarities = doc["similarities"]
if config.show>0:
    console.log("[bold red] Showing {}/{} of best similarities found".format(min(config.show, len(similarities)), len(similarities)))
    console.log(sorted(similarities, key=lambda x: calculateScore(x))[-config.show:])
for g in config.groups:
    console.log("[bold red] Groups by {}".format(g))
    console.log(sorted(createGroups(similarities, g), key=len))
