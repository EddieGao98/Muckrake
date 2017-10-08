import json

senate = open("senate.json", "r").read()
output = json.loads(senate)
print(output['results'][0]['members'])