# Name: ucget.py
# Desc: Import Manager - the ucget module
# Date: 2011.04.15
# Note:

import string
import core

def run(key,user=None):
    try:
        return string.join(core.ucget(key,user),',')
    except Exception as e:
        return "ERR_UCGET"
