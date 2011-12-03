#!/usr/bin/python
# Name: IlAbout.py (Input Language - About Widget)
# Desc: A widget including the SCIM info, triggered by the "About" btn.
# Date: 2010.03.24 - 1st release
#       2010.06.17 - 2nd release, rewrite to separate functionality widgets to individual files
# Note: 1.Usage:
#         import IlAbout
#         ...
#         IlAbout.Dialog([the parent's window])
#         ...
# Depend: 1.va-config.st2.0
#         2.bs-scim_simf

import pygtk
pygtk.require('2.0')
import gtk
import gettext
import gobject
import pango
import os
import IlUtil

#---constant variables---

HelpVaCmd="/bin/help-va"
ScimIconPath="/usr/share/pixmaps/scim-setup.png"
ScimIconSize=30

AboutW=320 #about window width
AboutH=300 #about window height

#---class---

class Dialog:
    def delete_event(self,widget,event,data=None):
        return False

    def destroy(self,widget,data=None):
        return False

    #when help link is pressed
    def onLinkPressed(self,widget,data=None):
        os.system(HelpVaCmd)

    #when close btn is pressed
    def onClosePressed(self,widget,data=None):
        self.window.destroy()

    def __init__(self,parentWin=None):

        #---ui initiailize---
        
        #initiailize locale
        gettext.bindtextdomain(IlUtil.RcDomain,IlUtil.LocaleDir)
        gettext.textdomain(IlUtil.RcDomain)
        gettext.install(IlUtil.RcDomain,IlUtil.LocaleDir,unicode=1)

        #create window
        window=gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event",self.delete_event)
        window.connect("destroy",self.destroy)
        window.set_size_request(-1,AboutH)
        window.set_resizable(False)
        window.set_modal(True)
        window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        window.set_title(_("About SCIM"))
        if parentWin!=None:
            window.set_transient_for(parentWin)
        self.window=window

        #main box
        mainBox=gtk.VBox(False,IlUtil.padW*2)
        mainBox.set_border_width(IlUtil.padW*2)
        self.window.add(mainBox)

        #titleSet
        titleBox=gtk.HBox(False)
        titleIcon=gtk.Image()
        titlePb=gtk.gdk.pixbuf_new_from_file_at_size(ScimIconPath,ScimIconSize,ScimIconSize)
        titleIcon.set_from_pixbuf(titlePb)
        titleBox.pack_start(titleIcon,False,False)
        titleLb=gtk.Label(_("<b>Input Language</b>"))
        titleLb.set_use_markup(True)
        titleBox.pack_start(titleLb,False,False)
        mainBox.pack_start(titleBox,False,False)

        #copyright
        crLb=gtk.Label(_("Smart Common Input Method\n Copyright 2002 - 2004, James Su<suzhe@tsinghua.org.cn>"))
        crLb.set_line_wrap(True)
        crAlign=gtk.Alignment(0,0,0,0)
        crAlign.add(crLb)
        mainBox.pack_start(crAlign,False,True)

        #hot key frame
        hkFm=gtk.Frame(_("Hot-Keys"))
        mainBox.pack_start(hkFm,False,False)
        hkBox=gtk.VBox(False,IlUtil.padW)
        hkBox.set_border_width(IlUtil.padW)
        hkFm.add(hkBox)
        triLb=gtk.Label(_("<b>Trigger:</b> Control + Space"))
        triLb.set_use_markup(True)
        triAlign=gtk.Alignment(0,0.5,0,0)
        triAlign.add(triLb)
        hkBox.pack_start(triAlign,False,True)
        nextLb=gtk.Label(_("<b>Next Input Method:</b> Control + Shift"))
        nextLb.set_use_markup(True)
        nextAlign=gtk.Alignment(0,0.5,0,0)
        nextAlign.add(nextLb)
        hkBox.pack_start(nextAlign,False,True)
        prevLb=gtk.Label(_("<b>Previous Input Method:</b> Shift + Control"))
        prevLb.set_use_markup(True)
        prevAlign=gtk.Alignment(0,0.5,0,0)
        prevAlign.add(prevLb)
        hkBox.pack_start(prevAlign,False,True)

        #link
        linkEb=gtk.EventBox()
        linkEb.connect("button_press_event",self.onLinkPressed)
        linkAlign=gtk.Alignment(0,0,0,0)
        linkAlign.add(linkEb)
        mainBox.pack_start(linkAlign,True,True)
        linkLb=gtk.Label(_("<u><span foreground=\"blue\">To Learn more about Input Language Setup, click here.</span></u>"))
        linkLb.set_line_wrap(True)
        linkLb.set_use_markup(True)
        linkEb.add(linkLb)

        #create separator
        sepBtm=gtk.HSeparator()
        sepBtm.set_size_request(AboutW,3)
        mainBox.pack_start(sepBtm,False,False)
     
        #close btn
        closeBtn=gtk.Button(_("Close"))
        closeBtn.set_size_request(IlUtil.btnW,IlUtil.btnH)
        closeBtn.connect("button_press_event",self.onClosePressed)
        closeAlign=gtk.Alignment(1,0.5,0,0)
        closeAlign.add(closeBtn)
        mainBox.pack_start(closeAlign,False,True)

        # show all ui
        self.window.show_all()

