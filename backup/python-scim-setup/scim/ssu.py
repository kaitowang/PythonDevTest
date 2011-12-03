# Name: ssu.py
# Desc: SCIM setup utility
# Date: 2011.03.24
# Note:

import os
import sys
import shutil
import textwrap
import types
from configobj import ConfigObj
from stos.toolutil import TuExcept, ERR

#ssu path definition
class PATH:
    USER_SCIM_DIR = "~/.scim"
    SYS_SCIM_DIR = "/etc/scim"
    SETUP_UTIL_DIR = "/setup-utils"
    INIT_CONF = "/init.conf"
    FIRSTRUN_CONF = "/firstrun.conf"
    DEFAULT_IMLIST_CONF = "/default_imlist.conf"

#ssu settings definition
class ST:
    #read/write permission tag
    FORBIDDEN = 0
    READ = 1
    WRITE = 1<<1

    #setting table column tag
    FILE = 0 #file to store the setting
    RW = 1 #read/write permission
    TYPE = 2 #return value type
    HELP = 3 #help comments

    #return value type tag
    BOOL = 0 #1/0
    STR = 1 #string
    LIST = 2 #a string separated by comma.

    #setting table
    TABLE={
        'enable_scim':
        [PATH.INIT_CONF,READ|WRITE,BOOL,
        '1 if SCIM is enabled by default, i.e., SCIM can be triggered \
by pressing [Ctrl]+[Space], otherwise 0.'],
        'lang_list':
        [PATH.FIRSTRUN_CONF,READ,LIST,
        'SCIM is enabled by default in the first boot if the system \
locale is listed in lang_list.'],
        'enable_default_imlist':
        [PATH.FIRSTRUN_CONF,READ,BOOL,
        '1 if we want to setup the default IM list in the first boot, \
otherwise 0.'],
        'imlist':
        [PATH.DEFAULT_IMLIST_CONF,READ,LIST,
        'The default IM list for a particular locale. You must assgin a \
locale LANG when you query this setting. If there is no default IM list \
for given locale, a empty string is returned.']
    }

class BaseOp:
    def doOp(cls,config,key,value=None):
        #pure virtual function, you should implement it.
        pass
    def checkOp(cls,rw_type,key,lang=None,value=None):
        #setup path
        user_ssu_dir=\
            os.path.expanduser(PATH.USER_SCIM_DIR+PATH.SETUP_UTIL_DIR)
        user_init_conf=user_ssu_dir+PATH.INIT_CONF
        sys_init_conf=\
            PATH.SYS_SCIM_DIR+PATH.SETUP_UTIL_DIR+PATH.INIT_CONF
        sys_firstrun_conf=\
            PATH.SYS_SCIM_DIR+PATH.SETUP_UTIL_DIR+PATH.FIRSTRUN_CONF
        sys_default_imlist_conf=\
            PATH.SYS_SCIM_DIR+PATH.SETUP_UTIL_DIR+PATH.DEFAULT_IMLIST_CONF
        if key not in ST.TABLE.keys():
            #invalid key
            raise TuExcept(ERR.INPUT,"Invalid SETTING: %s"%key)
        setting_file=ST.TABLE[key][ST.FILE]
        setting_rw=ST.TABLE[key][ST.RW]
        if setting_rw&rw_type==0:
            #not readable
            if rw_type==ST.READ:
                raise TuExcept(ERR.INPUT,
                    "The option %s is not readable."%key)
            elif rw_type==ST.WRITE:
                raise TuExcept(ERR.INPUT,
                    "The option %s is not writeable."%key)
            else:
                raise TuExcept(ERR.INTERNAL,
                    "The unknown RW %s."%rw_type)
            return
        if key=='imlist':
            config=ConfigObj(sys_default_imlist_conf)
            if lang==None:
                raise TuExcept(ERR.INPUT,
                    "LANG must be assigned when querying 'imlist'.")
            if lang not in config.keys():
                #invalid lang
                #raise TuExcept(ERR.INPUT,"Invalid LANG: %s"%lang)
                return []
            return cls.doOp(config,lang,value)
        else:
            if setting_file==PATH.INIT_CONF:
                #check user init conf first
                if not os.path.exists(user_ssu_dir):
                    os.makedirs(user_ssu_dir)
                if not os.path.exists(user_init_conf):
                    shutil.copy(sys_init_conf,user_ssu_dir)
                config=ConfigObj(user_init_conf)
            else:
                #firstrun conf
                config=ConfigObj(sys_firstrun_conf)
            return cls.doOp(config,key,value)

class GetOp(BaseOp):
    def doOp(cls,config,key,value=0):
        if key not in config.keys():
            raise TuExcept(ERR.INTERNAL,
                "GetOp: The key %s is not in config."%key)
        rtnval=config[key]
        if type(rtnval)==types.ListType:
            return rtnval
        else:
            rtnlist=[]
            rtnlist.append(rtnval)
            return rtnlist
    def run(cls,key,lang):
        return cls.checkOp(ST.READ,key,lang)

class SetOp(BaseOp):
    def doOp(cls,config,key,value):
        if key not in config.keys():
            raise TuExcept(ERR.INTERNAL,
                "SetOp: The key %s is not in config."%key)
        config[key]=value
        config.write()
    def run(cls,key,lang,value):
        cls.checkOp(ST.WRITE,key,lang,value)

def list(rw_show):
    print "Available settings:"
    keys=[]
    for key in ST.TABLE.keys():
        rw=ST.TABLE[key][ST.RW]
        if rw&rw_show!=0:
            keys.append(key)
    if len(keys)==0:
        print "No setting is available."
        return
    keys.sort()
    for key in keys:
        print ""
        print key
        type=ST.TABLE[key][ST.TYPE]
        type_str=""
        if type==ST.BOOL:
            type_str="(1/0)"
        elif type==ST.STR:
            type_str="(string)"
        elif type==ST.LIST:
            type_str="(string, a list separated with comma)"
        else:
            raise TuExcept(ERR.INTERNAL,
                "The unknown ST.TYPE %s."%type)
        rw=ST.TABLE[key][ST.RW]
        rw_str=""
        if rw==ST.READ:
            rw_str="[read-only]"
        elif rw==ST.WRITE:
            rw_str="[write-only]"
        elif rw==ST.READ|ST.WRITE:
            rw_str="[read/write]"
        else:
            raise TuExcept(ERR.INTERNAL,
                "The unknown ST.RW%s."%rw)
        help_list=textwrap.wrap(type_str+" "+rw_str+" "+\
                                ST.TABLE[key][ST.HELP])
        for text in help_list:
            print "    "+text

def get(key,lang=None):
    getop=GetOp()
    return getop.run(key,lang)

def set(key,value,lang=None):
    setop=SetOp()
    setop.run(key,lang,value)
    return value 

