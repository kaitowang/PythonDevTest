# Name: ssuget.py
# Desc: SCIM setup utility - the ssuget module
# Date: 2011.03.24
# Note:

import string
import ssu

def run(key,lang=None):
    try:
        return string.join(ssu.get(key,lang),',')
    except Exception as e:
        return "ERR_SSUGET"
