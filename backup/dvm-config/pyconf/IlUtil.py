#!/usr/bin/python
# Name: IlUtil.py
# Desc: The constants and utility functions using in the Input Language Configure Panel
# Date: 2010.03.24 - 1st release
#       2010.06.17 - 2nd release, rewrite to separate functionality widgets to individual files
# Depend: 1.va-config.st2.0
#         2.bs-scim_simf

import os
import Util
import VAEnv

import simf

#---constant variables---

#paths
LangKeyMapPath="/etc/oem/LangKeyMap"
InputLangListPath="/usr/share/maps/InputLangList"

#locale
RcDomain="dvm-config-input-lang"
LocaleDir="/usr/share/locale"

#Ui sizes
mainW=500 #main window width
mainH=360 #main window height

topH=60 #top area height
botH=50 #bottom area height
midH=mainH-topH-botH #middle area height

sepW=3 #separator width
padW=3 #padding space width

sideW=60 #side width(from window side to frame)
inputLangW=mainW-2*sideW #input language set width

btnW=75 #button width
btnH=25 #button height

#English IM uuid
EnglishImUuid="c6bebc27-6324-4b77-8ad4-6d41dcaf2e08"

#im detail setup module dictionary{uuid:module}
SetupModuleDic={
    "065d7b20-dda2-47fb-8f94-3306d9a25e56" : "anthy-imengine-setup.so",
    "fcff66b6-4d3e-4cf2-833c-01ef66ac6025" : "chewing-imengine-setup.so",
    "05235cfc-43ce-490c-b1b1-c5a2185276ae" : "pinyin-imengine-setup.so",
    "d75857a5-4148-4745-89e2-1da7ddaf70a9" : "hangul-imengine-setup.so",
    "63752e02-c9cb-420c-bac6-f17f60a16822" : "thai-imengine-setup.so"
}

#save mode
(
    NS, #Normal Save: The configure would not be saved until the user presses OK button to confirm.
    IS, #Instant Save: The configure would be saved when it is modified.
    DIS #Disable Instant Save: To disable Instant Save temporarily.
)=range(3)

#input method combobox columns
(
    LangCol,
    IconCol,
    NameCol,
    FunCol
)=range(4)

#page type
(
    AddRmImPage,
    ToolbarPage
)=range(2)

#treeview column
(
    IconCol,
    NameCol,
    EnableCol,
    IncCol,
    UuidCol
)=range(5)

#im info data
(
    InfoUuid,
    InfoName,
    InfoLocale,
    InfoIcon,
    InfoPri
)=range(5)

#---functions---

#convert language(English) to locale(en_US) 
def convertLangToLocale(langStr):
    localeStr=None
    langListPath=InputLangListPath
    if os.path.exists(langListPath):
        fp=Util.open_file(langListPath,"r")
        for line in fp.readlines():
            if line[0]=="\n" or line[0]=="#":
                continue
            line=line.strip()
            items=line.split(";")
            if items[0]==langStr:
                localeStr=items[1]
                break
        fp.close()
    if localeStr==None: #if there is no matched language, return "~other"
        return "~other"
    return localeStr

#convert locale(en_US) to language(English)
def convertLocaleToLang(localeStr):
    langStr=None
    langListPath=InputLangListPath
    if os.path.exists(langListPath):
        fp=Util.open_file(langListPath,"r")
        for line in fp.readlines():
            if line[0]=="\n" or line[0]=="#":
                continue
            line=line.strip()
            items=line.split(";")
            if items[1]==localeStr:
                langStr=items[0]
                break
        fp.close()
    if langStr==None: #if there is no matched locale, return "Other"
        return "Other"
    return langStr

#get input language list 
def getInputLangList():
    ilEnv=os.getenv("DI_DEF_INPUTLANG_LIST")
    availableIl=None
    if ilEnv != None:
        availableIl=ilEnv.split(',')
    else:
        #use all of input language
        availableIl=None
    langList=None
    langListPath=InputLangListPath
    if os.path.exists(langListPath):
        langList=[]
        fp=Util.open_file(langListPath,"r")
        for line in fp.readlines():
            if line[0]=="\n" or line[0]=="#":
                continue
            items=line.split(";")
            if availableIl:
                if items[0] in availableIl:
                    langList.append(items[0])
            else:
                langList.append(items[0])
    return langList

#get keyboard list
def getKeyboardList():
    kbList=VAEnv.di_have_key_list()
    if kbList:
        #modify keyboard name
        if "Arabic(001)" in kbList:
            kbList.remove("Arabic(001)")
            kbList.append("Arabic (001)")
        if "Arabic(002)" in kbList:
            kbList.remove("Arabic(002)")
            kbList.append("Arabic (002)")
        if "Czech(QWERTY)" in kbList:
            kbList.remove("Czech(QWERTY)")
            kbList.append("Czech (QWERTY)")
        if "Polish(programmers)" in kbList:
            kbList.remove("Polish(programmers)")
            kbList.append("Polish (programmers)")
        if "Portuguese(Brazilian ABNT)" in kbList:
            kbList.remove("Portuguese(Brazilian ABNT)")
            kbList.append("Portuguese (Brazilian ABNT)")
        if "Slovak(QWERTY)" in kbList:
            kbList.remove("Slovak(QWERTY)")
            kbList.append("Slovak (QWERTY)")
        kbList.sort()
    else:
        kbList=None
    return kbList

#get default keyboard with the given language
def getDefaultKbWithLang(langStr):
    kbStr=None
    if os.path.exists(LangKeyMapPath):
        fp=Util.open_file(LangKeyMapPath,"r")
        for line in fp.readlines():
            if line[0]=="\n" or line[0]=="#":
                continue
            line=line.strip()
            items=line.split(":")
            if items[0]==langStr:
                kbList=getKeyboardList()
                if items[1] in kbList:
                    return items[1]
                else:
                    return "English U.S."       
    return "English U.S."       
 
#get the im info list with given lang
def getImInfoDicWithLang(langStr,filter="enabled"):
    localeStr=convertLangToLocale(langStr)
    simf.init()
    simf.readcache(localeStr)
    imListStr=simf.listim(localeStr,filter)
    imList=imListStr.split(",")
    imInfoDic={}
    for uuid in imList:
        imInfoStr=simf.getinfo(uuid,localeStr)
        imInfo=imInfoStr.split(",")
        imInfoDic[uuid]=imInfo
        #covert pri from string to int
        imInfoDic[uuid][InfoPri]=int(imInfoDic[uuid][InfoPri],10)
    return imInfoDic

#write im infos to simf
def writeImInfo(oriSortedUuidList,curSortedUuidList,langStr):
    #init simf
    localeStr=convertLangToLocale(langStr)
    simf.init()
    simf.readcache(localeStr)
    #deal with disabled im
    for uuid in oriSortedUuidList:
        if uuid not in curSortedUuidList:
            simf.disableim(uuid,"flush",localeStr)
    #deal with enabled im
    for uuid in curSortedUuidList:
        simf.setmaxpri(uuid,"flush",localeStr)

#get the uuid which has the max priority
def getUuidWithMaxPri(inputImInfoDic):
    uuidList=inputImInfoDic.keys()
    priList=[inputImInfoDic[uuid][InfoPri] for uuid in uuidList]
    priToUuidDic=dict([[priList[i],uuidList[i]] for i in range(len(priList))])
    return priToUuidDic[max(priList)]

#set given im with max priority
def setUuidWithMaxPri(inputUuid,inputImInfoDic,langStr):
    uuidList=[]
    priList=[]
    if inputImInfoDic=={} or inputImInfoDic==None:
        maxPri=0
    else:
        uuidList=inputImInfoDic.keys()
        priList=[inputImInfoDic[uuid][InfoPri] for uuid in uuidList]
        maxPri=max(priList)
    if inputUuid not in uuidList:
        #get info of this im from simf and add this im's info in ImInfoDic 
        localeStr=convertLangToLocale(langStr)
        simf.init()
        simf.readcache(localeStr)
        imInfoStr=simf.getinfo(inputUuid,localeStr)
        imInfo=imInfoStr.split(",")
        inputImInfoDic[inputUuid]=imInfo
    inputImInfoDic[inputUuid][InfoPri]=maxPri+1
    return inputImInfoDic

#disable given im by removing it from imInfoDic
def disableImWithUuid(inputUuid,inputImInfoDic):
    if inputUuid in inputImInfoDic:
        del inputImInfoDic[inputUuid]
    return inputImInfoDic

