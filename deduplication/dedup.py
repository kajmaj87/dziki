# -*- coding: utf-8 -*-
import spacy
import json
import glob
from rich.console import Console
from rich.progress import track
from rich.traceback import install

install(show_locals=True)
console = Console()

TEXT_MIN_LENGHT = 10


with console.status("[bold green]Loading nlp model...") as status:
    nlp = spacy.load("pl_core_news_md")

console.log(nlp.Defaults.stop_words)

data = []
for f in glob.glob("data/*0.json"):
    with open(f, "r", encoding="utf8") as json_file:
        data.extend(json.load(json_file)["results"])

docs = []
withText, withComment, withTextAndComment = 0, 0, 0
for d in data:
    if len(d["comment"]) > TEXT_MIN_LENGHT or len(d["text"]) > TEXT_MIN_LENGHT:
        docs.append(
            {
                "id": d["id"],
                "nlpt": nlp(d["text"]),
                "text": d["text"],
                "nlpc": nlp(d["comment"]),
                "comment": d["comment"],
                "dup": d["is_duplicate"],
                "verdict": d["current_verdict"],
            }
        )
    withText += 1 if len(d["text"]) > TEXT_MIN_LENGHT else 0
    withComment += 1 if len(d["comment"]) > TEXT_MIN_LENGHT else 0
    withTextAndComment += 1 if len(d["comment"]) > TEXT_MIN_LENGHT and len(d["text"]) > TEXT_MIN_LENGHT else 0


similarities = []
for i, dx in track(enumerate(docs), "Processing", len(docs)):
    for j, dy in enumerate(docs):
        if j > i:
            simt = (
                dx["nlpt"].similarity(dy["nlpt"])
                if len(dx["text"]) > TEXT_MIN_LENGHT and len(dy["text"]) > TEXT_MIN_LENGHT
                else 0
            )
            if simt > 0 and (dx["verdict"] == "false" or dx["verdict"] == "true"):
                simc = (
                    dx["nlpc"].similarity(dy["nlpc"])
                    if len(dx["comment"]) > TEXT_MIN_LENGHT and len(dy["comment"]) > TEXT_MIN_LENGHT
                    else 0
                )
                simt = simt if simt < 1 else 2
                similarities.append(
                    (
                        simt,
                        simc,
                        simt ** 2 + simc ** 2,
                        dx["id"],
                        "Dup:" + str(dx["dup"]) + "_v:" + dx["verdict"],
                        dy["id"],
                        "Dup:" + str(dy["dup"]) + "_v:" + dy["verdict"],
                        dx["text"],
                        dy["text"],
                        dx["comment"],
                        dy["comment"],
                    )
                )

console.log(sorted(similarities, key=lambda x: x[2])[-500:])
print("Done. Total records: {}".format(len(similarities)))
print("Total: {} Text: {} Comment: {} T&C: {}".format(len(data), withText, withComment, withTextAndComment))
