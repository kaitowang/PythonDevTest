# Name: ssuget.py
# Desc: SCIM setup utility - the ssuset module
# Date: 2011.03.31
# Note:

import string
import ssu

def run(key,value):
    try:
        return ssu.set(key,value)
    except Exception as e:
        return "ERR_SSUSET"
