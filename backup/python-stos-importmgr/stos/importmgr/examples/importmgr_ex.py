#! /usr/bin/env python
# Name: importmgr_ex.py
# Desc: A example to use importmgr modules
# Date: 2011.04.15
# Note:

import stos.importmgr.core
import stos.importmgr.ucget
#import stos.importmgr.ucset

#---stos.importmgr module examples---

#stos.importmgr.core.ucget examples: 
#1. query the global setting
print stos.importmgr.core.ucget('auto_login')
print stos.importmgr.core.ucget('bookmark_path')
print stos.importmgr.core.ucget('default_login_user')
print stos.importmgr.core.ucget('defconf')
print stos.importmgr.core.ucget('enable_guest')
print stos.importmgr.core.ucget('region')
print stos.importmgr.core.ucget('timezone')
print stos.importmgr.core.ucget('user_list')
print stos.importmgr.core.ucget('wifi_path')
#2. query the user setting
#if you query a user setting without giving a account id, 
#importmgr return the setting for the current user
print stos.importmgr.core.ucget('account_display_name')
print stos.importmgr.core.ucget('account_enabled')
print stos.importmgr.core.ucget('account_id')
print stos.importmgr.core.ucget('account_uuid')
print stos.importmgr.core.ucget('remember_password')
print stos.importmgr.core.ucget('user_folder')
#3. query the user setting with a giving user.
#print stos.importmgr.core.ucget('account_display_name','the_account_id_for_the_user')
#4. raise an exception if a error occurs
#print stos.importmgr.core.ucget('invalid_setting')
print stos.importmgr.core.ucget('ro_user_music')
print stos.importmgr.core.ucget('ro_user_document')
print stos.importmgr.core.ucget('ro_user_video')
print stos.importmgr.core.ucget('ro_user_picture')

#importmgr.core.ucset examples: 
#!!!For now, importmgr.core.ucset is not supported.
#!!!You must run importmgr.core.ucset with root.
#1. set the global setting
#print stos.importmgr.core.ucset('auto_login','0')
print stos.importmgr.core.ucget('auto_login')
#print stos.importmgr.core.ucset('auto_login','1')
print stos.importmgr.core.ucget('auto_login')
#2. set the user setting
#if you set a user setting without giving a account id, 
#importmgr modify the setting for the current user
#print stos.importmgr.core.ucset('account_enabled','0')
print stos.importmgr.core.ucget('account_enabled')
#print stos.importmgr.core.ucset('account_enabled','1')
print stos.importmgr.core.ucget('account_enabled')
#3. query the user setting with a giving user.
#print stos.importmgr.core.ucset('account_enabled','0','the_account_id_for_the_user')
#4. raise an exception if a error occurs
#print stos.importmgr.core.ucset('invalid_setting')

#importmgr.list examples:
#to show the readable settings
stos.importmgr.core.list(stos.importmgr.core.ST.READ)

#---ucget module examples---

#1. query the global setting
print stos.importmgr.ucget.run('auto_login')
print stos.importmgr.ucget.run('bookmark_path')
print stos.importmgr.ucget.run('default_login_user')
print stos.importmgr.ucget.run('defconf')
print stos.importmgr.ucget.run('enable_guest')
print stos.importmgr.ucget.run('region')
print stos.importmgr.ucget.run('timezone')
print stos.importmgr.ucget.run('user_list')
print stos.importmgr.ucget.run('wifi_path')
#2. query the user setting
#if you query a user setting without giving a account id, 
#importmgr return the setting for the current user
print stos.importmgr.ucget.run('account_display_name')
print stos.importmgr.ucget.run('account_enabled')
print stos.importmgr.ucget.run('account_id')
print stos.importmgr.ucget.run('account_uuid')
print stos.importmgr.ucget.run('remember_password')
print stos.importmgr.ucget.run('user_folder')
#3. query the user setting with a giving user.
#print stos.importmgr.ucget.run('account_display_name','the_account_id_for_the_user')
print stos.importmgr.ucget.run('ro_user_music')
print stos.importmgr.ucget.run('ro_user_document')
print stos.importmgr.ucget.run('ro_user_video')
print stos.importmgr.ucget.run('ro_user_picture')
#4. print ERR_UCGET if a error occurs
print stos.importmgr.ucget.run('invalid_setting')

#---ucset module examples---

#!!!For now, the ucset module is not supported.
#!!!You must run ucset with root.
#1. set the global setting
#print stos.importmgr.ucset.run('auto_login','0')
print stos.importmgr.ucget.run('auto_login')
#print stos.importmgr.ucset.run('auto_login','1')
print stos.importmgr.ucget.run('auto_login')
#2. set the user setting
#if you set a user setting without giving a account id, 
#importmgr modify the setting for the current user
#print stos.importmgr.ucset.run('account_enabled','0')
print stos.importmgr.ucget.run('account_enabled')
#print stos.importmgr.ucset.run('account_enabled','1')
print stos.importmgr.ucget.run('account_enabled')
#3. query the user setting with a giving user.
#print stos.importmgr.ucset.run('account_enabled','0','the_account_id_for_the_user')
#4. raise an exception if a error occurs
#print stos.importmgr.ucset.run('invalid_setting')

