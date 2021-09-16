#!/usr/bin/python3

# For converting text to xml file
import id2xml as idx
from id2xml import run as idxrun
from id2xml import parser as idxparser

# To download rfc file in text format
import requests as req

# use of 'sys' module for command line arguments 
import sys
import os

def usage(cmd, error):
    print (error + "\nUsage: " + cmd + " <rfc id>")
  
# command line arguments are stored in the form 
# of list in sys.argv 
argumentList = sys.argv 

# Print the first argument after the name of file
if len(sys.argv) == 1:
    usage (sys.argv[0], "No RFC id given")
    exit (-1)

rfcid = sys.argv[1]
rtf = "rfc" + rfcid + ".txt"
rxf = "rfc" + rfcid + ".xml"
rcf = "rfc" + rfcid + ".csv"
rhf = "rfc" + rfcid + ".html"

def run_idx2xml():
    turl = "https://tools.ietf.org/rfc/rfc" + rfcid + ".txt"

    rt = req.get(turl, allow_redirects=True)

    try:
        os.remove(rtf)
        os.remove(rxf)
        os.remove(rcf)
        os.remove(rhf)
    except:
        pass

    rtfobj = open(rtf, "wb+")
    rtfobj.write(rt.content)

    sys.argv = ['', '-3', '--doc-stream', 'IETF', '--doc-consensus', rfcid, '--quiet', '-o'+rxf, rtf]

    ## Uncomment below line for running id2xml program in debug mode.
    sys.argv = ['',  '-3', '--doc-stream', 'IETF', '--doc-consensus', rfcid, '-d', '-o'+rxf, '-v', rtf]
    idxrun.run()
    rtfobj.close()

def document_minimal(x):
    x.postprocess()
    if x.options.schema == 'v3':
        xmlrfc = XmlRfc(lxml.etree.ElementTree(x.root), None)
        xmlrfc.source = x.name
        v3 = V2v3XmlWriter(xmlrfc)
        v3.convert2to3()
        x.root = v3.root
    return x.root

try:
    print("Staring")
    run_idx2xml()
except RuntimeError as rte:
    print("Ignoring runtime error ", rte)
    idxparser.DraftParser.document = document_minimal
    try:
        run_idx2xml()
    except RuntimeError as rtei:
        print(rte)
        pass
    pass

class RFCReq:
    header = ['ReqID', 'Section', 'Section Description', 'Requirement', 'Type', 'Reference']
    def __init__(self, reqid, sec, secname, requirement, kw, ref):
        self.reqid = reqid;
        self.sec = sec
        self.secname = secname
        self.requirement = requirement
        self.kw = kw
        self.ref = ref
        self.htmlref = "<a href=\"" + ref + "\">" + ref + "</a>"

reqlist = []

#import xml.etree.ElementTree as ET
import lxml.etree as ET
xmlparser = ET.XMLParser(recover=True)
rxtree = ET.parse(rxf, parser=xmlparser)
rxroot = rxtree.getroot()
keywords = ["MUST-NOT", "MUST", "REQUIRED", "SHALL-NOT", "SHALL", "SHOULD-NOT", "SHOULD", "RECOMMENDED-NOT", "RECOMMENDED", "MAY", "OPTIONAL"]

reqpattern = "RFC" + rfcid + "_REQID_"
reqcount = 0

dbgflag = False
def dbgprint(*values):
    if dbgflag:
        print(values)

def getsection(node):
    par = node
    while (par != None):
        if (par.tag != 'section'):
            par = par.getparent()
        else:
            return par

# for rxchild in rxtree.iter('section'):
#     sectag =  rxchild.get('anchor').replace('sect', '#section')
#     secdesc = rxchild.find('name')
for sub in rxtree.iter():
    dbgprint("SUB Details : ", sub.tag, sub.attrib, 0 if sub.text == None else len(sub.text.strip()), sub.text)
    if (sub.tag != 'artwork' and sub.tag != 'sourcecode' and sub.tag != 'xref' and sub.tag != 'section'):
        psec = getsection(sub)
        if (psec == None):
            continue
        sectag = psec.get('anchor').replace('sect', '#section')
        secdesc = psec.find('name').text

        if (sub.text != None and len(sub.text.strip()) > 0):
            req = (sub.text)
            for xr in sub.iter('xref'):
                req = (req + " " + xr.get('target') + " " + xr.tail)
            req = req.replace('\n', ' ').replace('    ', ' ')
            req = req.strip(' \t\n\r')
            req = req.replace('MUST NOT', 'MUST-NOT')
            req = req.replace('SHALL NOT', 'SHALL-NOT')
            req = req.replace('SHOULD NOT', 'SHOULD-NOT')
            req = req.replace('NOT RECOMMENDED', 'RECOMMENDED-NOT')
            dbgprint("REQ : ", req)
            prev = 0
            if all(key in req for key in keywords):
                continue
            for kw in keywords:
                pos = req.find(kw)
                if (pos > 0 and pos != prev):
                    prev = pos
                    reqcount += 1
                    reqlist.append(RFCReq(reqpattern + str(reqcount), sectag, secdesc, req, kw, "https://tools.ietf.org/rfc/rfc" + rfcid + sectag))

import csv
reqcsvf = open(rcf, 'w', newline='', encoding='utf-8')
csvwriter = csv.writer(reqcsvf)

colnames = RFCReq.header
csvwriter.writerow(colnames)

reqlistrows = []
for req in reqlist:
    row = []
    row.append(req.reqid)
    row.append(req.sec)
    row.append(req.secname)
    row.append(req.requirement)
    row.append(req.kw)
    row.append(req.ref)
    csvwriter.writerow(row)
#    row.pop()
#    row.append(req.htmlref)
    reqlistrows.append(row)

reqcsvf.close()

from tabulate import tabulate
 
htmlheader = """<html><head><style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
}

td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}

tr:nth-child(even) {
    background-color: #dddddd;
}
</style>
</head>"""
reqhtmlf = open(rhf, 'w', newline='', encoding='utf-8')
reqhtmlf.write(htmlheader)
reqhtmlf.write(tabulate(reqlistrows, colnames, tablefmt='html'))
reqhtmlf.close()
