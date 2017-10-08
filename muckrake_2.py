from crpapi import CRP
import sys
#from argparse import ArgumentParser

CRP.apikey = 'dbca3ef1d3c4b55075f276e533840579'
crp = CRP()

def analyze_congressman(congressional_id):
    candContribs = crp.candContrib.get(cid=congressional_id)
    contribs = {}
    output = ""
    index = 0
    for contributor in candContribs:
        #contribs[str(contributor[u'@attributes'][u'org_name'])] = float(contributor[u'@attributes'][u'total'])
        index += 1
        output = output + "\n" + str(contributor[u'@attributes'][u'org_name']) + '\t'\
                 + contributor[u'@attributes'][u'total']
    output = str(index) + output
    """indContribs = crp.candIndustry.get(cid=congressional_id)
    industry_contribs = {}
    for industry in indContribs:
        output = output + "\n" + str(industry[u'@attributes'][u'industry_name']) + '\t'\
                 + str(float(industry[u'@attributes'][u'indivs']) + float(industry[u'@attributes'][u'indivs']))
        #industry_contribs[str(industry[u'@attributes'][u'industry_name'])] = \
            #float(industry[u'@attributes'][u'pacs']) + float(industry[u'@attributes'][u'indivs'])"""
    print output

def main(cid):
    analyze_congressman(cid)

if __name__ == '__main__':
    main(
        sys.argv[1]
    )
