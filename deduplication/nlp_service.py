# -*- coding: utf-8 -*-
import spacy
import json
from bottle import run, post, request, response
from rich.progress import track

print("Loading nlp model")
nlp = spacy.load("pl_core_news_md")
print("Nlp model loaded, waiting for requests")

TEXT_MIN_LENGHT = 10


def processDocumentPair(dx, dy, nlpx, nlpy):
    simt = nlpx.similarity(nlpy) if len(dx["text"]) > TEXT_MIN_LENGHT and len(dy["text"]) > TEXT_MIN_LENGHT else 0
    if simt > 0:
        simt = simt if simt < 1 else 2
        return {"similarity": simt, "docs": [dx, dy]}


@post("/process")
def my_process():
    req = json.loads(request.body.read())
    docs = req["documents"]
    config = req["config"]
    similarities = []
    processedTexts = []
    for i, d in track(enumerate(docs), "Preprocessing", len(docs)):
        processedTexts.append(nlp(d["text"]))

    print("Processing {} documents...".format(len(docs)))
    for i, dx in track(enumerate(docs), "Processing", len(docs)):
        for j, dy in enumerate(docs):
            if j > i:
                processed = processDocumentPair(dx, dy, processedTexts[i], processedTexts[j])
                if processed is not None and processed["similarity"] > config["minSimilarity"]:
                    similarities.append(processed)
    print("Done.")
    return {"similarities": sorted(similarities, key=lambda x: x["similarity"])}


run(host="localhost", port=8080, debug=True)
