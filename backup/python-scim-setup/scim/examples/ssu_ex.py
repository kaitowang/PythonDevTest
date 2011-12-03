#! /usr/bin/env python
# Name: ssu_ex.py
# Desc: A example to use ssu modules
# Date: 2011.03.30
# Note:

import scim.ssu
import scim.ssuget
import scim.ssuset

#---ssu module examples---

#ssu.get examples: 
print scim.ssu.get('enable_scim')
print scim.ssu.get('lang_list')
print scim.ssu.get('enable_default_imlist')
print scim.ssu.get('imlist','zh_TW')
#arise an exception if a error occurs
#print scim.ssu.get('invalid_setting')

#ssu.set examples: 
#note that if you uncomment the following line and run this example,
#it will change the settings in the current system.
#scim.ssu.set('enable_scim','0')
print scim.ssu.get('enable_scim')
#scim.ssu.set('enable_scim','1')
print scim.ssu.get('enable_scim')

#ssu.list examples:
#to show the readable settings
scim.ssu.list(scim.ssu.ST.READ)

#---ssuget module examples---

print scim.ssuget.run('enable_scim')
print scim.ssuget.run('lang_list')
print scim.ssuget.run('enable_default_imlist')
print scim.ssuget.run('imlist','zh_TW')
#print ERR_SSUGET if a error occurs
print scim.ssuget.run('invalid_setting')

#---ssuset module examples---

#note that if you uncomment the following line and run this example,
#it will change the settings in the current system.
#print scim.ssuset.run('enable_scim','0')
print scim.ssuget.run('enable_scim')
#print scim.ssuset.run('enable_scim','1')
print scim.ssuget.run('enable_scim')
#print ERR_SSUSET if a error occurs
print scim.ssuset.run('invalid_setting','value')
