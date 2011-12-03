#! /usr/bin/env python
# Name: toolutil_ex.py
# Desc: a example to use the toolutil
# Date: 2011.03.25
# Note:

import sys

from stos.toolutil import *

#---macros---

#TOOL_NAME(string):
#The tool name. 
#This name would be used when creating a temporary directory.
TOOL_NAME='toolutil_ex'

#TOOL_VERSION(string):
#Version information. Usually use the date of your last commit.
TOOL_VERSION='20110414'

#DEBUG_MODE(bool):
#True to enable debug mode(to show all messages), otherwise False.
DEBUG_MODE=False

#MSG_MASK(msg_type_list, a bitwise expression of message types):
#Don't show the messages unless the DEBUG_MODE is True if their type is
#listed in msg_type_list. Note that msg_type_list is a bitwise-expression
#of message types.
MSG_MASK=MSG.DD#MSG.ALL^MSG.NL

#ERR_STR(string): the string which is printed when an error occurs.
ERR_STR='ERR_TUTEST'

if __name__ == '__main__':
    #Test TuCore
    tu=TuCore(TOOL_NAME,TOOL_VERSION,MSG_MASK,DEBUG_MODE)
    try:
        print tu.get_name()
        print tu.get_version()
        print tu.get_debug_mode()
        print tu.get_msg_mask()
        tu.create_temp()
        print tu.get_temp_dir()
        tu.print_msg(MSG.DD,
            "This message is not shown because DD is in MSG_MASK.")
        tu.print_msg(MSG.II,
            "This message is shown because II is not in MSG_MASK.")
        tu.print_msg(MSG.NL,
            "This message is shown without any message tags, i.e., the \
original print behavior.")
        tu.set_msg_mask(MSG.ALL^MSG.NL)
        tu.print_msg(MSG.II,
            "This message is not shown because II is in the message mask \
now.")
        tu.set_debug_mode(True)
        tu.print_msg(MSG.DD,
            "This message is shown when the debug mode is enabled.")
        if len(sys.argv) > 1:
            raise TuExcept(ERR.INTERNAL,
                "Give an argument to raise a internal error.")
        tu.print_msg(MSG.II,
            "If the debug mode is enabled, the temporary data is kept.")
        #test TuMsg
        tumsg=TuMsg(MSG_MASK,DEBUG_MODE)
        print tumsg.get_debug_mode()
        print tumsg.get_msg_mask()
        tumsg.print_msg(MSG.DD,
            "Test TuMsg - This message is not shown because DD is in the \
MSG_MASK.")
        tumsg.print_msg(MSG.II,
            "Test TuMsg - This message is shown because II is not in \
MSG_MASK.")
        tumsg.print_msg(MSG.NL,
            "Test TuMsg - This message is shown without any message tags, \
i.e., the original print behavior.")
        tumsg.set_msg_mask(MSG.ALL^MSG.NL)
        tumsg.print_msg(MSG.II,
            "Test TuMsg - This message is not shown because II is in the \
message mask now.")
        tumsg.set_debug_mode(True)
        tumsg.print_msg(MSG.DD,
            "Test TuMsg - This message is shown when the debug mode is \
enabled.")
        tu.quit_tool(0)
    except TuExcept as e:
        tu.print_msg(MSG.EE,e.error_msg)
        tu.print_msg(MSG.NL,ERR_STR)
        tu.quit_tool(e.error_type,True)
    except Exception as e:
        tu.print_msg(MSG.EE,"Unknown exception: %r"%(e))
        tu.print_msg(MSG.NL,ERR_STR)
        tu.quit_tool(ERR.UNKNOWN,True)

