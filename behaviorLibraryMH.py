import os
import os.path
import re
from xml.dom import minidom
import operator

################
# constants

## constants
dataPath = '/Users/histed/data/mus-behavior/MWVariables-backups';
exptName = 'HoldAndDetectConstant8';

rootGitPath = '_Users_holdanddetect_ExperimentXML-git';
fullEName = ('%s_HoldAndDetectConstant_%s' %
             (rootGitPath, exptName))


################

def getVariablesFromXmlFile(inFileName):
    with open(inFileName) as fh:
        m = minidom.parse(fh)

    m0 = m.getElementsByTagName('variable_assignments')[0] # should only be one in the file
    varNames = [a.attributes.getNamedItem('variable').value for a in m0.childNodes]
    varVals = [a.attributes.getNamedItem('value').value for a in m0.childNodes]
    vDict = dict(zip(varNames, varVals))

    return vDict

################

def getVariablesBySubject(subjNum, dateSpec=None, xmlName=None):

    ## get date specs from the on-disk directory
    allDateDirs = os.listdir(dataPath)

    if dateSpec is None or (not dateSpec):
        tDir = os.path.join(dataPath, allDateDirs[-1], fullEName, 'Saved Variables')
    else:
        raise RuntimeError, 'Need to implement date parsing'

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
    vDict = getVariablesFromXmlFile(fullXmlName)

    ## format it nicely and print it
    print '** %s' % xmlDiskName

    sortDict = sorted(vDict.items(), key=operator.itemgetter(0))
    for (varName, val) in sortDict:
        print '  %-35s: %7s' % (varName, val)




