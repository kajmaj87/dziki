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


c = http.client.HTTPConnection("localhost", 8080)
d = {"documents": loadDocuments(), "config": {"minSimilarity": 0.95}}
c.request("POST", "/process", json.dumps(d))
doc = json.loads(c.getresponse().read())
console.log(doc)
