from argparse import ArgumentParser
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from congress import Congress
import six
import sys
import json
import urllib
import html2text
from google.cloud import language_v1beta2
from google.cloud.language_v1beta2 import enums as enums2
from google.cloud.language_v1beta2 import types as types2
import subprocess
import google
import nltk
import wptools

congress = Congress('gt6jsrJY8cXmh6WmRYwK0820BFfrtZlf25fJSKlo')

def get_bill(id, session):
    url = 'https://api.propublica.org/congress/v1/%s/bills/%s.json' % (session, id)
    headers = {'X-API-Key': 'gt6jsrJY8cXmh6WmRYwK0820BFfrtZlf25fJSKlo'}
    req = urllib.request.Request(url, None, headers)
    response = urllib.request.urlopen(req).read()
    billinfo = json.loads(response)['results'][0]
    chamber = ""
    if billinfo['bill_type'][0] == 'h':
        chamber= 'house'
    elif billinfo['bill_type'][0] == 's':
        chamber = 'senate'
    sponsor_funding_list = get_congressman(billinfo['sponsor'], chamber)

    cosponsors_funding_lists = {}
    cosponsor_url = 'https://api.propublica.org/congress/v1/%s/bills/%s/cosponsors.json' % (session, id)
    cosponsor_headers = {'X-API-Key': 'gt6jsrJY8cXmh6WmRYwK0820BFfrtZlf25fJSKlo'}
    cosponsor_req = urllib.request.Request(cosponsor_url, None, cosponsor_headers)
    cosponsor_response = urllib.request.urlopen(cosponsor_req).read()
    cosponsor_list = json.loads(cosponsor_response)['results'][0]['cosponsors']
    for cosponsor in cosponsor_list:
        cosponsors_funding_lists[cosponsor['name']] = get_congressman(cosponsor["name"], chamber)
    funding_list = dict(cosponsors_funding_lists)
    funding_list[billinfo['sponsor']] = sponsor_funding_list

    if chamber == 'house':
        bill_url = 'https://www.gpo.gov/fdsys/pkg/BILLS-' + str(session)\
               + str(id) + 'ih/html/BILLS-' + str(session) + str(id) + 'ih.htm'
    elif chamber == 'senate':
        bill_url = 'https://www.gpo.gov/fdsys/pkg/BILLS-' + str(session) \
                   + str(id) + 'is/html/BILLS-' + str(session) + str(id) + 'is.htm'
    bill_headers = {'User-Agent': 'Mozilla/5.0'}
    bill_req = urllib.request.Request(bill_url, None, bill_headers)
    bill_response = urllib.request.urlopen(bill_req).read().decode("utf-8")
    keywords, categories = parse_text(html2text.html2text(bill_response))

    words_to_check = []
    #hypernyms = []
    for word in keywords:
        try:
            if include(word) and ' ' not in word:
                syn = nltk.corpus.wordnet.synsets(word)
                words_to_check = words_to_check + syn
                """paths = syn.hypernym_paths()
                for path in paths:
                    hypernyms = hypernyms + path"""
            else:
                lst = word.strip().split(' ')
                for w in lst:
                    if include(word):
                        syn = nltk.corpus.wordnet.synsets(w)
                        words_to_check = words_to_check + syn
                        """paths = syn.hypernym_paths()
                        for path in paths:
                            hypernyms = hypernyms + path"""
        except(nltk.corpus.reader.wordnet.WordNetError):
            dummy = None
    syn_words = []
    for synword in words_to_check:
        word = synword.name().strip().split(".")[0].replace("_", " ")
        if include(word):
            syn_words.append(word)
    words_to_check = set([word for word in keywords if include(word)] + syn_words)

    relevant_list = {}
    for sponsor in funding_list:
        sponsor_relevant_list = {}
        if funding_list[sponsor] != None and funding_list[sponsor][0] != None:
            for company in funding_list[sponsor][0]:
                try:
                    wikipage = wptools.page(company.replace(" ", "_"))
                    pagedata = wikipage.get_query().data['extext']
                    for word in words_to_check:
                        if word in pagedata:
                            sponsor_relevant_list[company] = funding_list[sponsor][0][company]

                    language_client = language_v1beta2.LanguageServiceClient()
                    document = types2.Document(
                        content=pagedata,
                        type=enums2.Document.Type.PLAIN_TEXT
                    )
                    result = language_client.classify_text(document)
                    for category in result.categories:
                        flag = False
                        for bill_category in categories:
                            if category.name in bill_category or bill_category in category.name:
                                flag = True
                    if flag == True:
                        sponsor_relevant_list[company] = funding_list[sponsor][0][company]
                except(LookupError):
                    dummy = None
            relevant_list[sponsor] = sponsor_relevant_list
    print(json.dumps(relevant_list, indent=4, separators=(',', ': ')))
    return relevant_list

def include(word):
    excluded = ("sense", "amount", "enact", "congress", "mr.", "ms.", "mrs.", "government",
               "u.s.", "united states", "obligation", "limit", "committee", "senate", "house", "resolution", "report",
               "plan", "act", "section", "s.con", "h.con", "facility", "facilities", "paragraph", "subsection", "staff",
               "title", "document", "purpose", "rule", "state", "department", "secretary", "submit", "term", "title",
               "along")
    for e in excluded:
        if e in word or word in e:
            return False
    return True

def get_congressman(name, chamber):
    if chamber == 'senate':
        senatejson = open("senate.json", "r")
        senate = json.load(senatejson)['results'][0]['members']
        for senator in senate:
            if (senator['first_name'] + ' ' + senator['last_name']) == name:
                """python3_command = "muckrake_2.py '" + senator['crp_id'] + "'"
                process = subprocess.Popen(python3_command.split(), stdout=subprocess.PIPE, shell=True)
                output, error = process.communicate()  # receive output from the python2 script"""
                output = subprocess.check_output(["python2", "muckrake_2.py", senator['crp_id']]).decode('utf-8')
                return str_to_dict(output)
    elif chamber == 'house':
        housejson = open("house.json", "r")
        house = json.load(housejson)['results'][0]['members']
        for rep in house:
            if (rep['first_name'] + ' ' + rep['last_name']) == name:
                """python3_command = "muckrake_2.py '" + rep['crp_id'] + "'"
                process = subprocess.Popen(python3_command.split(), stdout=subprocess.PIPE, shell=True)
                output, error = process.communicate()  # receive output from the python2 script"""
                output = subprocess.check_output(["python2", "muckrake_2.py", rep['crp_id']]).decode('utf-8')
                return str_to_dict(output)

def str_to_dict(str):
    lines_list = str.splitlines()
    contribs = {}
    industry_contribs = {}
    for i in range(1, int(lines_list[0]) + 1):
        line = lines_list[i].strip().split('\t')
        contribs[line[0]] = float(line[1])
    """for i in range(int(lines_list[0]) + 1, len(lines_list)):
        line = lines_list[i].strip().split('\t')
        industry_contribs[line[0]] = float(line[1])"""
    #return [contribs, industry_contribs]
    return [contribs, []]

def parse_text(text):
    client = language.LanguageServiceClient()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    document = types.Document(
        content=text.encode('utf-8'),
        type=enums.Document.Type.PLAIN_TEXT)

    # Detect and send native Python encoding to receive correct word offsets.
    encoding = enums.EncodingType.UTF32
    if sys.maxunicode == 65535:
        encoding = enums.EncodingType.UTF16
    result = client.analyze_entity_sentiment(document, encoding)

    keywords = []
    categories = []

    for entity in result.entities:
        """print('Mentions: ')
        print(u'Name: "{}"'.format(entity.name))
        for mention in entity.mentions:
            print(u'  Begin Offset : {}'.format(mention.text.begin_offset))
            print(u'  Content : {}'.format(mention.text.content))
            print(u'  Magnitude : {}'.format(mention.sentiment.magnitude))
            print(u'  Sentiment : {}'.format(mention.sentiment.score))
            print(u'  Type : {}'.format(mention.type))
        print(u'Salience: {}'.format(entity.salience))
        print(u'Sentiment: {}\n'.format(entity.sentiment))"""
        for mention in entity.mentions:
            if mention.sentiment.score > 0 and entity.name not in keywords:
                    keywords.append(entity.name.lower())

    sections = text.strip().split("SEC.")
    language_client = language_v1beta2.LanguageServiceClient()
    for section in sections:
        subsections = section.strip().split("    (")
        for i in range(0, len(subsections)):
            subsection = subsections[i]
            if len(subsection) > 750:
                document = types2.Document(
                    content=subsection.encode('utf-8'),
                    type=enums2.Document.Type.PLAIN_TEXT
                )
                result = language_client.classify_text(document)
                for category in result.categories:
                    categories.append(category.name)
            else:
                if i < len(subsections) - 1:
                    subsections[i+1] = subsections[i] + " " + subsections[i+1]
    return keywords, categories

def main(bill, session):
    return get_bill(bill, session)

if __name__ == '__main__':
    main(
        sys.argv[1], sys.argv[2]
    )
