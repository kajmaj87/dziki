#!/bin/bash

for p in {1..130}
do
  echo "Fetching page $p"
  # paste real curl below
  curl --compressed > data/pap_page$p.json
done
