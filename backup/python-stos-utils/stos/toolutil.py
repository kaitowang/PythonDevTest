#Name: toolutil.py
#Desc: A set of classes for a python tool script.
#Date: 2011.03.25

import sys
import os
import shutil
import tempfile

#---classes---

#message type constants
class MSG:
    NONE = 0 #None of them
    NL = 1 #Normal(No msg tag)
    DD = 1<<1 #Debug
    II = 1<<2 #Information
    WW = 1<<3 #Warning
    EE = 1<<4 #Error
    ALL = NL|DD|II|WW|EE #all types

#error type constants
class ERR:
    INPUT = 1 #Invalid inputs
    FILE_IO = 2 #An error occurs when reading/writing a file
    INTERNAL = 254 #An internal error occurs
    UNKNOWN = 255 #An unknown error occurs

class TuExcept(Exception):
    """\
TuExcept - The exception class

    Contain more information in an exception.

"""
    def __init__(cls,type,msg):
        cls.error_type=type
        cls.error_msg=msg

class TuMsg:
    """\
TuMsg- The message class 

    This class provides a message handler which has following features: 
    1. Addtional message tags.
    2. Use the mask to control the message display.

"""
    def __init__(cls,input_msg_mask,input_debug_mode=False):

        #---private variables---
        cls._msg_mask=input_msg_mask
        cls._debug_mode=input_debug_mode

        #---init---
        pass

    #---public functions---

    def get_msg_mask(cls):
        return cls._msg_mask

    def get_debug_mode(cls):
        return cls._debug_mode

    def set_msg_mask(cls,value):
        cls._msg_mask=value

    def set_debug_mode(cls,value):
        cls._debug_mode=value

    def print_msg(cls,msg_type,msg_str):
        """\
print_msg- print messages in the running time.

Print messages with a given tag in the running time. Note that the
Debug messages is printed only when Debug mode is enabled.

Input:
msg_type(int[NL/DD/II/WW/EE]): the message type.
msg_str(string): the message string.

Return:
None

Example:
print_msg(DD, "This message is shown when the debug mode is enabled.")
print_msg(NL, "This message is shown without any message tags, i.e., the \
               original print behavior.")
        """
        #message string definition
        MSG_STR_DD="[DD]"
        MSG_STR_II="[II]"
        MSG_STR_WW="[WW]"
        MSG_STR_EE="[EE]"

        msg_output=""
        if msg_type==MSG.DD:
            msg_output=MSG_STR_DD+" "+msg_str
        elif msg_type==MSG.II:
            msg_output=MSG_STR_II+" "+msg_str
        elif msg_type==MSG.WW:
            msg_output=MSG_STR_WW+" "+msg_str
        elif msg_type==MSG.EE:
            msg_output=MSG_STR_EE+" "+msg_str
        else:
            msg_output=msg_str
        if (msg_type&cls._msg_mask)!=0 and not cls._debug_mode:
            return
        print msg_output

class TuCore:
    """\
TuCore - The core class 

    This class provides a source management which handles 
    1. The tool name, version and quit flow.
    2. The message printing.
    3. The temporary data used in a tool script.

"""
    def __init__(cls,input_name,input_ver,
                     input_msg_mask,input_debug_mode=False):

        #---private variables---
        cls._name=input_name
        cls._version=input_ver
        cls._debug_mode=input_debug_mode
        cls._msg_mask=input_msg_mask
        cls._temp_dir=""
        cls._msg_handler=TuMsg(cls._msg_mask,cls._debug_mode)

        #---init---
        pass

    #---public functions---

    def get_name(cls):
        return cls._name

    def get_version(cls):
        return cls._version

    def get_debug_mode(cls):
        return cls._debug_mode

    def get_msg_mask(cls):
        return cls._msg_mask

    def get_temp_dir(cls):
        if cls._temp_dir=="":
            raise TuExcept(ERR.INTERNAL,"A temporary directory hasn't \
been created. Please call \"create_temp()\" first.")
        return cls._temp_dir

    def set_debug_mode(cls,value):
        cls._debug_mode=value
        cls._msg_handler.set_debug_mode(value)

    def set_msg_mask(cls,value):
        cls._msg_mask=value
        cls._msg_handler.set_msg_mask(value)

    def print_msg(cls,msg_type,msg_str):
        cls._msg_handler.print_msg(msg_type,msg_str)

    def quit_tool(cls,quit_status,keep_temp=False):
        """\
quit_tool - quit the tool 

Ouput the quit messages and return the quit status.

Input:
quit_status(int[0/-1]): the quit status, 0 means the normal quit, \
                        nonzero means the abnormal quit.
keep_temp(bool): true to keep the temporary data, otherwis false.

Return:
None

Example:
quit_tool(0)
quit_tool(1,True)
        """
        if quit_status!=0:
            cls._msg_handler.print_msg(MSG.II,"An Error occurs!! Abort!!")
        if os.path.exists(cls._temp_dir):
            if cls._debug_mode or keep_temp:
                cls._msg_handler.print_msg(MSG.II,
                    "All logs and temporary data are stored in "
                    +cls._temp_dir)
            else:
                shutil.rmtree(cls._temp_dir)
        sys.exit(quit_status)

    def create_temp(cls):
        """\
create_temp - create a temporary directory

Create a temporary directory

Input:
None

Return:
(string) the temporary directory path

Example:
create_temp()
        """
        if cls._temp_dir!="":
            raise TuExcept(ERR.INTERNAL,
                "The temporary directory \"%s\" is already created."
                %(cls._temp_dir))
        else:
            cls._temp_dir=tempfile.mkdtemp("-toolutil-%s"%cls._name);
            if not os.path.exists(cls._temp_dir):
                raise TuExcept(ERR.INTERNAL,
                    "Cannot create a temporary directory.")

