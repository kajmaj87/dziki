#!/bin/bash

usage() {
  echo
  echo "Example usage:"
  echo "TOKEN=<copy from headers in news request> $0 <news id>"
  echo 
  echo "This pretty print one news with given id to be pretty printed in console"
}

if [[ -z "${TOKEN}" ]]; then
  echo "Please provide TOKEN env variable to use this script"
  usage
  exit 1
fi

if [[ -z "$1" ]]; then
  echo "Please provide news id as parameter"
  usage
  exit 1
fi

curl -s "https://panel-api.fakehunter.pap.pl/news/crew/expert/news/$1" \
  -H 'authority: panel-api.fakehunter.pap.pl' \
  -H 'pragma: no-cache' \
  -H 'cache-control: no-cache' \
  -H 'sec-ch-ua: "Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"' \
  -H 'accept: application/json, text/plain, */*' \
  -H "authorization: Token $TOKEN" \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36' \
  -H 'origin: https://panel.fakehunter.pap.pl' \
  -H 'sec-fetch-site: same-site' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-dest: empty' \
  -H 'referer: https://panel.fakehunter.pap.pl/' \
  -H 'accept-language: en-US,en;q=0.9,pl;q=0.8,de-DE;q=0.7,de;q=0.6,ca;q=0.5' \
  --compressed | python -m json.tool
