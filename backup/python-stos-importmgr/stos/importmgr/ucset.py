# Name: ucget.py
# Desc: Import Manager - the ugset module
# Date: 2011.04.15
# Note:

import string
import core

def run(key,value,user=None):
    try:
        return core.ucset(key,value,user)
    except Exception as e:
        return "ERR_UCSET"
