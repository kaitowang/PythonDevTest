#! /usr/bin/env python
# Name: parseini_ex.py
# Desc: a example to use the parseini
# Date: 2011.05.10
# Note:

import sys

from stos.parseini import ParseINIcp

parseini=ParseINIcp("./parseini_data.ini")
print parseini.getValue('S1','a')
print parseini.getKeyList('S2')
print parseini.getSessionList()
print parseini.getValue('S1','b')
#parseini.setValue('S1','b','22')
#parseini.writeINI()
print parseini.getValue('S1','b')

#parseini=ParseINIcp("./parseini_data.ini")
#print parseini.getValue('S1','a')
#print parseini.getKeyList('S2')
#print parseini.getSessionList()
#print parseini.getValue('S1','b')
##parseini.setValue('S1','b','22')
##parseini.writeINI()
#print parseini.getValue('S1','b')

