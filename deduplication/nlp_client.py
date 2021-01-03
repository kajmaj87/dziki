import http.client
import json
from glob import glob
from rich.console import Console
from rich.traceback import install

install(show_locals=True)

console = Console()


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
    return textScore**2 + commentScore**2

c = http.client.HTTPConnection("localhost", 8080)
d = {"documents": loadDocuments(), "fields": [{"name":"text", "min_similarity": 0.9, "min_length": 10, "boost_exact_match": False }, {"name":"comment", "min_length":10, "min_similarity": 0.9}]}
c.request("POST", "/process", json.dumps(d))
doc = json.loads(c.getresponse().read())
console.log(sorted(doc["similarities"], key=lambda x: calculateScore(x))[-200:])
