import gdata, gdata.spreadsheet.service
import getpass
import string; from string import *
import keyring
import mathMH as mMH
import pandas

import re
import numpy as np
from datetime import datetime
from matplotlib.dates import date2num

def extractDataFromSheetAsFrame(titleStr, username, doReAuth=False):
    """Returns a pandas dataFrame"""

    client = doSpreadsheetAuth(username, doReAuth=doReAuth)
    key = findKeyByTitle(client, titleStr)

    # get first worksheet name
    wF = client.GetWorksheetsFeed(key)
    wEntry = wF.entry[0]
    wId = wEntry.id.text.split('/')[-1]

    # get data by row
    r = client.GetListFeed(key, wksht_id=wId)


    # convert these to float
    waterV = mMH.convertToFloat([b.custom['workingwater'].text for b in r.entry])
    suppV = mMH.convertToFloat([b.custom['extraworkingsupplement'].text for b in r.entry])
    weightV = mMH.convertToFloat([b.custom['weight'].text for b in r.entry])
    nCorrects = mMH.convertToFloat([b.custom['correct'].text for b in r.entry])
    nTrials = mMH.convertToFloat([b.custom['trials'].text for b in r.entry])
    # extract as text
    date = [b.custom['date'].text for b in r.entry]
    mouse = [b.custom['subject'].text for b in r.entry]
    # refine animalNum
    animalNum = mMH.convertToFloat([re.findall('[Ii]([0-9]*)', b)[0] for b in mouse])
    # refine date
    dateT = [datetime.strptime(b, '%m/%d/%Y') for b in date]
    dateV = mMH.convertToFloat([date2num(b) for b in dateT])

    ## Construct data frame

    allD = { 'date': dateT, 
             'subjectNum': animalNum, 
             'weight': weightV,
             'water': waterV, 
             'supplement': suppV, 
             'nCorrects': nCorrects, 
             'nTrials': nTrials }
    dF = pandas.DataFrame(allD)

    return dF


def doSpreadsheetAuth(username, doReAuth=False):
    # get user and pass first
    serviceStr = 'GDocsWaterProcessor';
    password = keyring.get_password(serviceStr, username)
    if password is None or doReAuth == True:
        password = getpass.getpass("Enter your password: ")
        keyring.set_password(serviceStr, username, password)
    else:
        print('Using saved password')

    client = gdata.spreadsheet.service.SpreadsheetsService(email=username, password=password)
    try:
        client.ProgrammaticLogin()
    except gdata.service.BadAuthentication, e:
        print "Authentication error logging in: %s" % e
    except Exception, e:
        print "Error Logging in: %s" % e

    return client

def findKeyByTitle(client, titleStr):
  # Get the list of spreadsheets
  feed = client.GetSpreadsheetsFeed()

  for i, entry in enumerate(feed.entry):
      if lower(strip(entry.title.text)) == lower(strip(titleStr)):
          break
          
  return feed.entry[i].id.text.rsplit('/', 1)[1]
    


def PromptForSpreadsheet(gd_client):
  # Get the list of spreadsheets
  feed = gd_client.GetSpreadsheetsFeed()
  searchStr = 'training'
  PrintFeed(feed, searchStr)
  input = raw_input('\nSelection: ')
  return feed.entry[string.atoi(input)].id.text.rsplit('/', 1)[1]

def PrintFeed(feed, searchStr=None):
    
  for i, entry in enumerate(feed.entry):
    if searchStr is not None:
        if (string.find(string.lower(entry.title.text),
                       string.lower(searchStr))
            == -1):
            # not found
            continue
        
        
    if isinstance(feed, gdata.spreadsheet.SpreadsheetsCellsFeed):
      print '%s %s\n' % (entry.title.text, entry.content.text)
    elif isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
      print '%s %s %s' % (i, entry.title.text, entry.content.text)
      # Print this row's value for each column (the custom dictionary is
      # built from the gsx: elements in the entry.) See the description of
      # gsx elements in the protocol guide.
      print 'Contents:'
      for key in entry.custom:
        print '  %s: %s' % (key, entry.custom[key].text)
      print '\n',
    else:
      print '%s %s' % (i, entry.title.text)


def getDataForPlotting(username, spreadsheetTitle):
    """returns an object with fields that are numpy data vectors"""


    client = doSpreadsheetAuth(username)
    key = findKeyByTitle(client, spreadsheetTitle)
        
    # get first worksheet name
    wF = client.GetWorksheetsFeed(key)
    wEntry = wF.entry[0]
    wId = wEntry.id.text.split('/')[-1]
    
    # get data by row
    sheetFeed = client.GetListFeed(key, wksht_id=wId)
    
    r = sheetFeed

    class DataHolder(object):  # we will put fields onto this
        pass
    out = DataHolder()
    

    out.water = convertToFloat([b.custom['water'].text for b in r.entry])
    out.weight = convertToFloat([b.custom['weight'].text for b in r.entry])
    date = [b.custom['date'].text for b in r.entry]
    mouse = [b.custom['mouse'].text for b in r.entry]
    out.nCorrects = convertToFloat([b.custom['correct'].text for b in r.entry])
    out.nTrials = convertToFloat([b.custom['trials'].text for b in r.entry])
    
    out.animalNum = convertToFloat([re.findall('[Ii]([0-9]*)', b)[0] for b in mouse])
    
    out.dateT = [datetime.strptime(b, '%m/%d/%Y') for b in date]
    out.date = convertToFloat([date2num(b) for b in out.dateT])

    out.rmin = convertToFloat([b.custom['rmin'].text for b in r.entry])
    out.rmax = convertToFloat([b.custom['rmax'].text for b in r.entry])
    
    return out

