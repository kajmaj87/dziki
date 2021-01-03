# -*- coding: utf-8 -*-
from collections import defaultdict

import spacy
import json
from bottle import run, post, request, response
from rich.progress import track
from spacy.lang.pl.stop_words import STOP_WORDS

TEXT_MIN_LENGHT = 10


def processDocumentPair(nlpx, nlpy, boost=False):
    simt = nlpx.similarity(nlpy)
    if simt > 0:
        simt = 2 if simt >= 1 and boost else simt
        return simt


def processDocuments(nlp, docs, fields):
    similarities = []
    processedTexts = defaultdict(list)
    for i, d in track(enumerate(docs), "Preprocessing", len(docs)):
        for f in fields:
            if "stop_word_removal" in f and f["stop_word_removal"]:
                text = " ".join([w.lower() for w in d[f["name"]].split() if w not in STOP_WORDS])
            else:
                text = d[f["name"]]
            processedTexts[f["name"]].append(nlp(text))

    print("Processing {} documents...".format(len(docs)))
    for i, dx in track(enumerate(docs), "Processing", len(docs)):
        for j, dy in enumerate(docs):
            if j > i:
                document_similarities = {}
                for f in fields:
                    minLenght = f["min_length"] if "min_length" in f else 0
                    minSimilarity = f["min_similarity"] if "min_similarity" in f else 0
                    boost = f["boost_exact_match"] if "boost_exact_match" in f else False
                    fieldName = f["name"]

                    if len(dx[fieldName]) > minLenght and len(dy[fieldName]) > minLenght:
                        similarity = processDocumentPair(
                            processedTexts[fieldName][i], processedTexts[fieldName][j], boost
                        )
                        if similarity is not None and similarity > minSimilarity:
                            document_similarities[fieldName] = similarity
                if len(document_similarities) > 0:
                    similarities.append({"similarities": document_similarities, "docs": [dx, dy]})
    print("Done. Sending back {} records.".format(len(similarities)))
    return {"similarities": similarities}


@post("/process")
def my_process():
    req = json.loads(request.body.read())
    docs = req["documents"]
    fields = req["fields"]
    return processDocuments(nlp, docs, fields=fields)


if __name__ == "__main__":
    print("Loading nlp model")
    nlp = spacy.load("pl_core_news_md")
    print("Nlp model loaded, waiting for requests")
    run(host="localhost", port=8080, debug=True)
