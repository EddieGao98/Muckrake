import json
import urllib.request
from congress import Congress
import sys

def main(search_term):
    search_term = search_term.replace(" ", "+")
    url = 'https://api.propublica.org/congress/v1/bills/search.json?query=%s' % (search_term)
    headers = {'X-API-Key': 'gt6jsrJY8cXmh6WmRYwK0820BFfrtZlf25fJSKlo'}
    req = urllib.request.Request(url, None, headers)
    response = urllib.request.urlopen(req).read()
    print(response)
    return response

if __name__ == '__main__':
    main(
        sys.argv[1]
    )
