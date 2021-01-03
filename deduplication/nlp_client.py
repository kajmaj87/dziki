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
console.log(sorted(doc["similarities"], key=lambda x: calculateScore(x))[-config.show:])
