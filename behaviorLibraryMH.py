import os
import os.path
import re
import copy
from xml.dom import minidom
import string
import operator
import directoryConstants as dc; reload(dc)

################
# constants

dataPath = dc.varSyncDir
exptName = 'HoldAndDetectConstant8';

rootGitPath = '_Users_holdanddetect_ExperimentXML-git';
fullEName = ('%s_HoldAndDetectConstant_%s' %
             (rootGitPath, exptName))

################




class varDict:
    """To read vals from xml file: init with empty argument, then call getVariablesFromDisk"""
    xmlFileName = None
    dict = None  # must be initialized in init otherwise this is a class variable!!
    xmlTypeDict = None

    def __init__(self):
        self.dict = dict()
        self.xmlTypeDict = dict()

    def printVarDict(self):
        """format it nicely and print it"""

        sortDict = sorted(self.dict.items(), key=operator.itemgetter(0))

        if self.xmlFileName is not None:
            print '** %s' % self.xmlFileName

        for (varName, val) in sortDict:
            print '  %-35s: %7s' % (varName, val)
    
    def _getVariablesFromXmlFile(self, inFileName):
        """overwrites any current value in the dict"""

        with open(inFileName) as fh:
            m = minidom.parse(fh)

        m0 = m.getElementsByTagName('variable_assignments')[0] # should only be one in the file
        varNames = [a.attributes.getNamedItem('variable').value for a in m0.childNodes if a.nodeName != '#text']
        varVals = [a.attributes.getNamedItem('value').value for a in m0.childNodes if a.nodeName != '#text']
        varTypes = [a.attributes.getNamedItem('type').value for a in m0.childNodes if a.nodeName != '#text' ]
        self.dict = dict(zip(varNames, varVals))
        self.xmlTypeDict = dict(zip(varNames, varTypes))        
        self.xmlFileName = inFileName

    def getVariablesBySubject(self, subjNum, dateSpec=None, xmlName=None):
        """dateSpec: a string of form YYMMDD, 
        calls _getVariablesFromXml file, updating the dict"""

        ## get date specs from the on-disk directory
        allDateDirs = os.listdir(dataPath)

        if dateSpec is None or (not dateSpec):
            tDir = os.path.join(dataPath, allDateDirs[-1], fullEName, 'Saved Variables')
        else:
            dMatchList = [a for a in allDateDirs if re.search(dateSpec, a) is not None]
            if len(dMatchList) == 0:
                raise RuntimeError, 'Data for date %s not found' % dateSpec
            elif len(dMatchList) > 1: 
                raise RuntimeError, 'More than one variable match for date - bug?'
            else:
                tDir = os.path.join(dataPath, dMatchList[0], fullEName, 'Saved Variables')



        ## find the xml filename for the given subject num
        if xmlName is None or xmlName == '':
            allNames = os.listdir(tDir)
            matchList = [a for a in allNames if re.search('%d'%subjNum, a) is not None]

            if len(matchList) > 1:
                print matchList
                raise RuntimeError, 'More than one match found - look above and set xmlName'
            xmlDiskName = matchList[0]
        else:
            xmlDiskName = xmlName

        if re.match('\.xml$', xmlDiskName) is None:
            xmlDiskName = xmlDiskName + '.xml'

        fullXmlName = os.path.join(tDir, xmlDiskName)

        ## get the dict
        self._getVariablesFromXmlFile(fullXmlName)




################################################################
# non-class functions

def diffXmlTwoDates(subjNum, dateSpecBefore, dateSpecFinal=None, xmlName=None):
    """Returns: two var dicts: (changedDict, oldDict): same keys but oldDict
    contains the original values that have changed.  If not present this is None"""

    vD1 = varDict(); 
    vD1.getVariablesBySubject(subjNum, dateSpecBefore, xmlName=xmlName)
    vD2 = varDict();
    vD2.getVariablesBySubject(subjNum, dateSpecFinal, xmlName=xmlName)

    # compute diffs
    changedD = varDict()
    oldD = varDict()
    
    for (tK,tVal) in vD2.dict.iteritems():
        if not vD1.dict.has_key(tK):
            initVal = None
        elif vD1.dict[tK] != tVal:
            initVal = vD1.dict[tK]
        else:
            # matches, skip
            continue

        changedD.dict[tK] = tVal
        oldD.dict[tK] = initVal
        
    return (changedD,oldD)


def printChanges(changedD,oldD):
    
    #print changedD.dict
    #print oldD.dict
    sortOrig = sorted(copy.copy(changedD.dict).items(), key=operator.itemgetter(0))

    #print '** %s to %s'  % (oldD.xmlFileName, changedD.xmlFileName)

    for (varName, val) in sortOrig:
        print '  %-35s: %7s -> %7s' % (varName, oldD.dict[varName], val)


################

def getAllDatesByXmlName(xmlFileName):
    """Returns: a list of strings giving all dates for this xmlname.
    If xmlFileName is none, don't restrict by xml name"""

    if xmlFileName is not None and xmlFileName[-3:].lower() != "xml":
        xmlFileName = xmlFileName + '.xml'

    dirList = []
    for root, dirnames, filenames in os.walk(dataPath):
        # prune irrelevant dirs
        delList = [x for x in dirnames if (string.find(x,'_Users') == 0 and string.find(x,exptName)==-1)]
        if len(delList) > 0:
            for tL in delList:
                dirnames.remove(tL)

        if string.find(exptName, root):
            if xmlFileName is None or xmlFileName in filenames:
                dirList.append(root)

    rePat = '^.*MWVariables-backups/backup-after-sync-([0-9]*)/_Users_.*$'
    dateList = set()
    for tDir in dirList:
        tMatch = re.match(rePat, tDir)
        if tMatch is not None:
            dateList.update(tMatch.groups())

    dateList = sorted(dateList)
    return dateList


