import sys
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--normtaglist", help="Comma-separated list of normtag (e.g. 'nt1.json,nt2.json')")
parser.add_argument("-o", "--outputfile", default="compositeNT.json", help="output file name")

args=parser.parse_args()

# both args are list of lists where each list is a range of LSs
def RemoveLSs(baseList,listToRM):
    expandedBaseList=[]
    #print "baseList",baseList
    #print "listToRM",listToRM
    for lsRange in baseList:
        for iLS in range(lsRange[0],lsRange[1]+1):
            expandedBaseList.append(iLS)
    
    #print "added all",expandedBaseList
    for lsRange in listToRM:
        for iLS in range(lsRange[0],lsRange[1]+1):
            if iLS in expandedBaseList:
                expandedBaseList.remove(iLS)

    #print "removed some",expandedBaseList
    
    condensedList=[]
    lastLS=0
    for iLS in expandedBaseList:
        if iLS==expandedBaseList[0]:
            condensedList.append([iLS,-1])
        elif iLS-lastLS>1:
            condensedList[-1][1]=lastLS
            condensedList.append([iLS,-1])

        if iLS==expandedBaseList[-1]:
            condensedList[-1][1]=iLS
        lastLS=iLS

    #print condensedList
    return condensedList

normtagslist=args.normtaglist.split(",")

rankAlgo="Default"
print "This script will fill a new normtag with the contents of the given normtags."
if rankAlgo == "Default":
    print "The default ranking algo gives highest priority to the first normtag in the list and lowest priority to the last normtag in the list."


print normtagslist

normtags={}


for normtagfilename in normtagslist:
    ntfile=open(normtagfilename)
    normtags[normtagfilename]=json.load(ntfile)


compositeNT=[]
filledRuns=[]

if rankAlgo=="Default":
    print "go through NTs in the order received"
    print "fill in new list with luminometers if run,ls not covered"
    for normtagfilename in normtagslist:
        for line in normtags[normtagfilename]:
            run=line[1].keys()[0]
            lsRanges=line[1][line[1].keys()[0]]
            #print "run",run
            if not compositeNT:
                compositeNT.append(line)
            else:
                #print "find run in list--search whole list--run could be in more than one line"
                iLine=0
                for item in compositeNT:
                    comRun=item[1].keys()[0]
                    #print "if run found remove all LSs already covered"
                    if comRun==run:
                        #print "in com",item
                        #print "to be included",line    
                        lsRanges=RemoveLSs(lsRanges,item[1][run])
                        if not lsRanges:
                            break
                    elif comRun>run:
                        break
                    iLine=iLine+1
                if run not in filledRuns:
                    compositeNT.insert(iLine,line)
                elif lsRanges:
                    newDict={}
                    newDict[run]=lsRanges
                    compositeNT.insert(iLine,[line[0],newDict])
                
            filledRuns.append(run)


outputFile=open(args.outputfile,"w")
outputFile.write("[\n")
for line in compositeNT:
    #schade... ths simple way can't be decoded
    #outputFile.write(str(line))
    # example line:    ["hfoc16v1",{"271037":[[1,15]]}],
    outputFile.write("[\""+str(line[0])+"\",{\""+str(line[1].keys()[0])+"\":"+str(line[1][line[1].keys()[0]])+"}]")
    if line != compositeNT[-1]:
        outputFile.write(",\n")
        
outputFile.write("\n]\n")
outputFile.close()
