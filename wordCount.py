import sys
import os

def replace(string):
    string = string.lower()
    remove = ['\\r', '\\n', '!', ',', '.', '-', ';', ':', '%', '\"', '\\', '\'']
    for c in remove:
        if c in string:
            string = string.replace(c,' ')
    return string

def rf(arg1):
    f1 = open(arg1, "r")
    text = f1.read()
    text = replace(text)
    text = sorted(text.split())
    return toDic(text)

def toDic(fList):
    fDic = {}
    for word in fList:
        if word in fDic:
            fDic[word] += 1
        else:
            fDic[word] = 1
    return fDic

def writeDict(dic, fileName):
    for stuff, moreStuff in dic.items():
        fileName.write(stuff + " " + str(moreStuff) + "\n")

if len(sys.argv) is not 3:
    print("wrong number of arguments")
    exit()

textFile = sys.argv[1]
outputFile=sys.argv[2]

dic = rf(textFile)
#printDict(dic)

writeDict(dic, open(outputFile, "w"))

