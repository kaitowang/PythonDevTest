# Name: importmgr.py
# Desc: Import Manager
# Date: 2011.04.15
# Note:

import os
import sys
import shutil
import textwrap
import types
import string
from configobj import ConfigObj
from stos.toolutil import TuMsg, TuExcept, ERR, MSG

#importmgr path definition
class PATH:
    #IMPORTMGR_INI(string): the path of the import manager configure.
    #export_path is stored in this file.
    IMPORTMGR_INI="/etc/stos/importmgr/importmgr.ini"

    #STEXPORT_INI(string): the file path of STExport.ini
    # this path is relative to export_path
    STEXPORT_INI="/STExport.ini"

    #VAECONF_INI(string): the file path of vaeconf.ini
    # this path is relative to export_path
    VAECONF_INI="/dvmexp/VAECONF/vaeconf.ini"

    #ACCOUNTINFO_INI(string): the file name to store user settings
    # the file paths for each user are stored in the USERS session of 
    # STExport.ini
    ACCOUNTINFO_INI="accountInfo.ini"

#importmgr settings definition
class ST:
    #setting table column tag
    GU = 0 #global/user 
    RW = 1 #read/write permission
    TYPE = 2 #return value type
    FILE = 3 #file to store the setting
    TARGET = 4 #query target,it is a list = ['session','key']
    HELP = 5 #help comments

    #global/user tag
    GLOBAL = 0
    USER = 1

    #read/write permission tag
    FORBIDDEN = 0
    READ = 1
    WRITE = 1<<1
    #HIDDEN: it is only for stos-login-mgr usage, not shown on the list.
    HIDDEN = 1<<2

    #return value type tag
    BOOL = 0 #1/0
    STR = 1 #string
    LIST = 2 #a string separated by comma.
    OTHER = 3 #not one of the above.

    #setting table: a table to define all imported settings.
    #'setting':[GU,RW,TYPE,FILE,TARGET,HELP]
    TABLE={
        'default_login_user':
        [GLOBAL,READ,STR,PATH.STEXPORT_INI,
        ['General','default_login_user'],
        'Only for auto-login usage, use this account to login by \
default.'],
        'auto_login':
        [GLOBAL,READ,BOOL,PATH.STEXPORT_INI,
        ['General','auto_login'],
        '1 if auto-login is enabled(i.e. no login screen is shown), \
otherwise 0.'],
        'enable_guest':
        [GLOBAL,READ,BOOL,PATH.STEXPORT_INI,
        ['General','enable_guest'],
        '1 if a guest account is enabled, otherwise 0.'],
        'region':
        [GLOBAL,READ,STR,PATH.STEXPORT_INI,
        ['General','region'],
        'the region code(ISO 3166-1 numeric).'],
        'defconf':
        [GLOBAL,READ,STR,PATH.STEXPORT_INI,
        ['General','defconf'],
        'the locale(ISO 639 and ISO 3166-1 alpha-2).'],
        'timezone':
        [GLOBAL,READ,STR,PATH.VAECONF_INI,
        ['vaeconf','TimeZoneBiasToGMT'],
        'the time zone(UTC offset).'],
        'bookmark_path':
        [GLOBAL,READ,STR,PATH.IMPORTMGR_INI,
        ['path','bookmark_path'],
        'the directory path which stores the bookmark configure.'],
        'wifi_path':
        [GLOBAL,READ,STR,PATH.IMPORTMGR_INI,
        ['path','wifi_path'],
        'the directory path which stores the wifi configure.'],
        'user_list':
        [GLOBAL,READ,LIST,PATH.STEXPORT_INI,
        ['USERS'],
        'the account_id list.'],
        'account_id':
        [USER,READ,STR,PATH.ACCOUNTINFO_INI,
        ['ACCOUNT_INFO','account_id'],
        'the account id, same as the STOS account name.'],
        'account_display_name':
        [USER,READ,STR,PATH.ACCOUNTINFO_INI,
        ['ACCOUNT_INFO','account_display_name'],
        'the display name shown in the login screen.'],
        'account_uuid':
        [USER,READ,STR,PATH.ACCOUNTINFO_INI,
        ['ACCOUNT_INFO','account_uuid'],
        'the uuid.'],
        'user_folder':
        [GLOBAL,READ,STR,PATH.IMPORTMGR_INI,
        ['path','winusr_path'],
        'the user folder path in STOS.'],
        'real_user_folder':
        [USER,FORBIDDEN,STR,PATH.ACCOUNTINFO_INI,
        ['ACCOUNT_INFO','user_folder'],
        'the window user folder path in STOS.'],
        'account_enabled':
        [USER,READ,BOOL,PATH.ACCOUNTINFO_INI,
        ['ACCOUNT_INFO','account_enabled'],
        '1 if the account is enabled(the account is listed in the login \
screen), otherwise 0.'],
        'account_type':
        [USER,FORBIDDEN,OTHER,PATH.ACCOUNTINFO_INI,
        ['ACCOUNT_INFO','account_type'],
        '(0/1/2): the account type. 0: administrator, 1: normal user, 2: \
guest user. For now, only the normal user is created in DL2.0, i.e., \
it\'s value is always 1.'],
        'remember_password':
        [USER,READ,BOOL,PATH.ACCOUNTINFO_INI,
        ['ACCOUNT_INFO','remember_password'],
        '1 if the password is remembered(the user can login without \
typing password), otherwise 0.'],
        'ro_user_music':
        [USER,READ|HIDDEN,STR,PATH.ACCOUNTINFO_INI,
        ['ACCOUNT_INFO','user_music'],
        'the window music folder path in STOS(read only).'],
        'ro_user_picture':
        [USER,READ|HIDDEN,STR,PATH.ACCOUNTINFO_INI,
        ['ACCOUNT_INFO','user_picture'],
        'the window picture folder path in STOS(read only).'],
        'ro_user_video':
        [USER,READ|HIDDEN,STR,PATH.ACCOUNTINFO_INI,
        ['ACCOUNT_INFO','user_video'],
        'the window video folder path in STOS(read only).'],
        'ro_user_document':
        [USER,READ|HIDDEN,STR,PATH.ACCOUNTINFO_INI,
        ['ACCOUNT_INFO','user_document'],
        'the window document folder path STOS(read only).']
    }

class BaseOp:
    def __init__(cls,msg_mask,debug_mode):
        cls.tumsg=TuMsg(msg_mask,debug_mode)

    def do_op(cls,config,target,user=None):
        #pure virtual function, you should implement it.
        pass

    def check_op(cls,rw_type,setting,user=None,value=None):
        #get export and stos root paths
        if not os.path.exists(PATH.IMPORTMGR_INI):
            raise TuExcept(ERR.INTERNAL,
                "Cannot find the file \"%s\""%PATH.IMPORTMGR_INI)
        config=ConfigObj(PATH.IMPORTMGR_INI)
        path_data=config['path']
        cls.export_path=path_data['export_path']
        cls.stos_root_path=path_data['stos_root']
        cls.winusr_path=path_data['winusr_path']
        cls.stos_root_ro_path=path_data['stos_root_ro']
        cls.tumsg.print_msg(MSG.DD,"export_path=<%s>"%cls.export_path)
        cls.tumsg.print_msg(MSG.DD,"stos_root_path=<%s>"%cls.stos_root_path)
        cls.tumsg.print_msg(MSG.DD,"winusr_path=<%s>"%cls.winusr_path)
        cls.tumsg.print_msg(MSG.DD,"stos_root_ro_path=<%s>"%cls.stos_root_ro_path)

        #get setting info
        if setting not in ST.TABLE.keys():
            raise TuExcept(ERR.INPUT,"Invalid SETTING: %s"%setting)
        cls.setting=setting
        setting_gu=ST.TABLE[setting][ST.GU]
        setting_rw=ST.TABLE[setting][ST.RW]
        setting_file=ST.TABLE[setting][ST.FILE]
        setting_target=ST.TABLE[setting][ST.TARGET]
        cls.tumsg.print_msg(MSG.DD,"setting=<%s>"%cls.setting)
        cls.tumsg.print_msg(MSG.DD,"setting_gu=<%s>"%setting_gu)
        cls.tumsg.print_msg(MSG.DD,"setting_rw=<%s>"%setting_rw)
        cls.tumsg.print_msg(MSG.DD,"setting_file=<%s>"%setting_file)
        cls.tumsg.print_msg(MSG.DD,"setting_target=<%s>"%setting_target)

        #read/write permission check
        if setting_rw&rw_type==0:
            #not readable/writeable
            if rw_type==ST.READ:
                raise TuExcept(ERR.INPUT,
                    "The setting \"%s\" is not readable."%setting)
            elif rw_type==ST.WRITE:
                raise TuExcept(ERR.INPUT,
                    "The setting \"%s\" is not writeable."%setting)
            else:
                raise TuExcept(ERR.INTERNAL,
                    "The unknown RW \"%s\"."%rw_type)

        #here:check user id
        user_query=None
        user_path=None
        if setting_gu==ST.USER:
            stexport_path=cls.export_path+PATH.STEXPORT_INI
            cls.tumsg.print_msg(MSG.DD,
                "stexport_path=[%s]"%(stexport_path))
            if not os.path.exists(stexport_path):
                raise TuExcept(ERR.INTERNAL,
                    "Cannot find the file \"%s\""%stexport_path)
            config=ConfigObj(stexport_path)
            user_data=config['USERS']
            if user!=None:
                cls.tumsg.print_msg(MSG.DD,"user_data=<%r>"%(user_data))
                if user in user_data:
                    user_query=user
                    user_path=user_data[user_query]
                else:
                    raise TuExcept(ERR.INPUT,
                        "Invalid user id: %s."%user)
            if user_query==None:
                #query the current login user id
                general_setting=config['General']
                default_user=general_setting['default_login_user']
                if default_user==None:
                    raise TuExcept(ERR.INTERNAL,
                        "Cannot query the default login user id.")
                elif default_user not in user_data:
                    raise TuExcept(ERR.INTERNAL,
                        "The default login user id is not in USERS.")
                else:
                    user_query=default_user
            #window_path="C:\a\b\c" -> stos_path="{stos_root}/a/b/c"
            user_path=cls.stos_root_path+"/"+string.join(
                string.split(user_data[user_query],'\\')[1:],'/')
        cls.tumsg.print_msg(MSG.DD,"user_query=<%s>"%user_query)
        cls.tumsg.print_msg(MSG.DD,"user_path=<%s>"%user_path)

        #check file path
        file_path=None
        if setting_file==PATH.IMPORTMGR_INI:
            file_path=PATH.IMPORTMGR_INI
        elif setting_file==PATH.STEXPORT_INI or \
             setting_file==PATH.VAECONF_INI:
            file_path=cls.export_path+setting_file
        elif setting_file==PATH.ACCOUNTINFO_INI:
            file_path=user_path
        if not os.path.exists(file_path):
            raise TuExcept(ERR.INTERNAL,
                "Cannot find the file \"%s\""%file_path)
        cls.tumsg.print_msg(MSG.DD,"file_path=<%s>"%file_path)

        #read/write the setting
        config=ConfigObj(file_path)
        cls.tumsg.print_msg(MSG.DD,"config=<%r>"%config)
        return cls.do_op(config,setting_target,value)

class GetOp(BaseOp):
    def __init__(cls,msg_mask,debug_mode):
        BaseOp.__init__(cls,msg_mask,debug_mode)

    def do_op(cls,config,target,value=0):
        session=target[0]
        if session not in config.keys():
            raise TuExcept(ERR.INTERNAL,
                "GetOp: The session \"%s\" is not in config."%session)
        session_data=config[session]
        if len(target)==1:
            return session_data.keys()
        else:
            key=target[1]
            if key not in session_data.keys():
                raise TuExcept(ERR.INTERNAL,
                    "GetOp: The key \"%s\" is not in the session \"%s\"."
                    %(key,session))
            value=session_data[key]
            #modify output
            if cls.setting=='real_user_folder':
                #window_path="C:\a\b\c" -> stos_path="{stos_root}/a/b/c"
                value=cls.stos_root_ro_path+"/"+string.join(
                    string.split(value,'\\')[1:],'/')
            if cls.setting in ['ro_user_music',
                               'ro_user_document',
                               'ro_user_picture',
                               'ro_user_video']:
                if value=="":
                    raise TuExcept(ERR.INTERNAL,
                        "GetOp: The user folder path \"%s\" is empty."
                        %(key))
                else:
                    #window_path="C:\a\b\c" -> stos_path="{stos_root_ro}/a/b/c"
                    value=cls.stos_root_ro_path+"/"+string.join(
                        string.split(value,'\\')[1:],'/')
            #return value
            if type(value)==types.ListType:
                return value 
            else:
                rtnlist=[]
                rtnlist.append(value)
                return rtnlist

    def run(cls,setting,user):
        return cls.check_op(ST.READ,setting,user)

class SetOp(BaseOp):
    def __init__(cls,msg_mask,debug_mode):
        BaseOp.__init__(cls,msg_mask,debug_mode)

    def do_op(cls,config,target,value):
        session=target[0]
        if session not in config.keys():
            raise TuExcept(ERR.INTERNAL,
                "SetOp: The session \"%s\" is not in config."%session)
        session_data=config[session]
        if len(target)==1:
            raise TuExcept(ERR.INTERNAL,
                "SetOp: Cannot write data to a session.")
        else:
            key=target[1]
            if key not in session_data.keys():
                raise TuExcept(ERR.INTERNAL,
                    "SetOp: The key \"%s\" is not in the session \"%s\"."
                    %(key,session))
            session_data[key]=value
            config.write()

    def run(cls,setting,user,value):
        cls.check_op(ST.WRITE,setting,user,value)

def ucget(setting,user=None,msg_mask=MSG.ALL^MSG.NL,debug_mode=False):
    get_op=GetOp(msg_mask,debug_mode)
    return get_op.run(setting,user)

def ucset(setting,value,user=None,msg_mask=MSG.ALL^MSG.NL,debug_mode=False):
    set_op=SetOp(msg_mask,debug_mode)
    set_op.run(setting,user,value)
    return value 

#list(rw_show):list settings
def list(rw_show):

    def print_list(settings):
        if len(settings)==0:
            print "    No setting is available."
        else:
            settings.sort()
            for setting in settings:
                print "    "+setting
                type=ST.TABLE[setting][ST.TYPE]
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
                rw=ST.TABLE[setting][ST.RW]
                rw_str=""
                if rw==ST.READ:
                    rw_str="[read-only] "
                elif rw==ST.WRITE:
                    rw_str="[write-only]"
                elif rw==ST.READ|ST.WRITE:
                    rw_str="[read/write]"
                else:
                    raise TuExcept(ERR.INTERNAL,
                        "The unknown ST.RW \"%s\"."%rw)
                wrapper=textwrap.TextWrapper()
                wrapper.initial_indent="        "
                wrapper.subsequent_indent="        "
                help_list=wrapper.wrap(rw_str+" "+type_str+" "+\
                                       ST.TABLE[setting][ST.HELP])
                for text in help_list:
                    print text

    global_settings=[]
    user_settings=[]
    for setting in ST.TABLE.keys():
        rw=ST.TABLE[setting][ST.RW]
        gu=ST.TABLE[setting][ST.GU]
        if rw&rw_show!=0:
            if rw&ST.HIDDEN!=0:
                continue
            if gu==ST.GLOBAL:
                global_settings.append(setting)
            else:
                user_settings.append(setting)
    print "Global settings:"
    print ""
    print_list(global_settings)
    print ""
    print "User settings:"
    print ""
    print_list(user_settings)

