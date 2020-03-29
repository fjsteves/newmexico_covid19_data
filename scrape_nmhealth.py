#!/usr/bin/python3
# Created by Frank Steves
# Licensed for use in the GNU GPL v3.0 license.  Additional details can be found in the COPYING file with this software.
# Description:  This allows you to roll for ingredients based on real based used on the show Chopped by the Food Network
# Note: If for some reason the Wikipedia page changes the format, this will break in a bad way!
#

import argparse
import datetime
import hashlib
import operator
import os
import random
import re
import requests
import sys
import time

from bs4 import BeautifulSoup

ts = time.time()
nmhealth = "https://cv.nmhealth.org/cases-by-county" 
parser = argparse.ArgumentParser()

parser.add_argument("-p", "--print", help="Print's out current NMHealth case information", action="store_true", default=False)

args = parser.parse_args()

page = requests.get(nmhealth)
soup = BeautifulSoup(page.text, 'html.parser')

caseData = []

def pullData():
    
    caseCount = 0

    table = soup.find_all('table')[0]
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        caseData.append([ele for ele in cols if ele])

    deathCount = 0
    
    for case in caseData[1:]:
        if case[2] == "—":
            deathCount = 0
        else:
            deathCount = case[2]

        print ("{0},{1},{2},{3}".format(case[0], case[1], deathCount, datetime.datetime.fromtimestamp(ts).strftime('%m/%d/%Y')))

    for case in caseData[1:]:
        caseCount = caseCount + int(case[1])

    return caseCount


def hashGen(num):

    #TODO: Do we need this for any good reason now?
    sitehash = hashlib.sha1(str(page.text).encode()).hexdigest()
    totalcounthash = hashlib.sha1(str(pullData()).encode()).hexdigest()
    
    return (sitehash, totalcounthash)

        
def generateReport():

    #Work in Progress - TODO: Write this data out to a file instead of using STDOUT to make the files
    #Who cares about the hashing at this point....

    hashData = hashGen(pullData())

    #Write out data to a file
    hashDump = open("site-stats" + datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y'), "w")

    for hashes in hashData:
        hashDump.write(hashes + '\n')

    hashDump.close()

def monitorChange():

    oldSum = pullData()

    while True:    
        time.sleep(6)       
        newSum = pullData()
        
        print ("."),
        if oldSum == newSum:
            print (".",)
            continue
        else:
            print ("Numbers updated!")
            print ("Timestamp:", datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))

            for county, count in sorted(caseData)[1:]:
                print ("County: {0}\nCount {1}".format(county,count))

            print ("Total cases in New Mexico: {0}".format(newSum))

            break
            


#This is the real main loop, boys.  Bardownskis!
pullData()
#monitorChange()
