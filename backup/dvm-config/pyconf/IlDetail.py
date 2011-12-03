#!/usr/bin/python
# Name: IlDetail.py (Input Language - Detail Widget)
# Desc: A dialog showing the detail settings in some IMs(Chewing, Smart-Pinyin, Anthy, Korean and Thai),
#       triggered by the "..." btn.
# Date: 2010.03.24 - 1st release
#       2010.06.17 - 2nd release, rewrite to separate functionality widgets to individual files
# Depend: 1.va-config.st2.0
#         2.bs-scim_simf
# Note: 1.Usage:
#         import IlDetail
#         ...
#         def setDetailChange(self,inputUuid,result=True):
#         ...
#         IlDetail.DialogWidget(self,[IM setup module],[parent's window],[save mode])
#         ...
#
#       2.APIs:
#         (1)def setDetailChange(self,inputUuid,result=True):
#            Input:inputUuid(string) - the detail setting module's IM uuid.
#                  result(bool) - Ture if the settings are changed, otherwise False.
#            Output:None

#from pygtk
import pygtk
pygtk.require('2.0')
import gtk

#from std python
import gettext
import gobject
import pango
import os

#from config.st2.0
import Util
import Dialog

#from config.st2.0.input-lang
import IlUtil
import ssml

#---class---

class DialogWidget:
    #[API needed by pyconf.Dialog]deal with restartx event(write config and restart x)
    def restartx(self,reponse):
        if reponse=="Yes":
            #restartx
            cmd="bbdock -x %s/X_quit" %Util.PATH
            os.system(cmd)
        else:
            #destroy RX and the detail dialogs
            self.popup.dialog.destroy()

    def delete_event(self,widget,event,data=None):
        return False

    def destroy(self,widget,data=None):
        ssml.close()
        return False

    #when ok btn is pressed
    def onOkPressed(self,widget,data=None):
        if ssml.querychange():
            #save config
            ssml.saveconfig()
            if self.saveMode==IlUtil.IS:
                #close window first
                self.window.destroy()
                #trigger the "Restart X" Dialog
                self.popup=Dialog.dlgRestart(self)
                self.popup.dialog.set_title(_("Input Language"))
            else:
                self.parent.setDetailChange(self.uuid,True);
                self.window.destroy()
        else:
            self.window.destroy()

    #when cancel btn is pressed
    def onCancelPressed(self,widget,data=None):
        self.window.destroy()

    def __init__(self,parent,inputUuid,parentWin=None,inputSaveMode=IlUtil.NS):
        #---data initiailize---
        #init data
        self.saveMode=inputSaveMode
        self.parent=parent
        self.uuid=inputUuid
        #init ssml
        ssml.init(IlUtil.SetupModuleDic[self.uuid])
        #---ui initiailize---
        #initiailize locale
        gettext.bindtextdomain(IlUtil.RcDomain,IlUtil.LocaleDir)
        gettext.textdomain(IlUtil.RcDomain)
        gettext.install(IlUtil.RcDomain,IlUtil.LocaleDir,unicode=1)
        #create window
        window=gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event",self.delete_event)
        window.connect("destroy",self.destroy)
        window.set_size_request(IlUtil.mainW,IlUtil.mainH)
        window.set_resizable(False)
        window.set_modal(True)
        window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        window.set_title(_("Input Method Settings"))
        window.set_keep_above(True)
        if parentWin!=None:
            window.set_transient_for(parentWin)
        if inputSaveMode==IlUtil.IS:
            window.set_decorated(False)
        self.window=window
        #create main box
        mainBox=gtk.VBox(False)
        mainBox.set_border_width(IlUtil.padW)
        window.add(mainBox)
        #lable
        titleLb=gtk.Label(_(ssml.getname()))
        titleAlign=gtk.Alignment(0.5,0.5,0,0)
        titleAlign.add(titleLb)
        mainBox.pack_start(titleAlign,False,True)
        #setup widget
        self.setupWidget=ssml.getwidget()
        ssml.loadconfig()
        mainBox.pack_start(self.setupWidget)
        #create buttons box
        btnsBox=gtk.HBox(False,IlUtil.padW*3)
        btnsBox.set_size_request(IlUtil.mainW,IlUtil.botH)
        btnsBox.set_border_width(IlUtil.padW*3)
        mainBox.pack_start(btnsBox,False,False)
        #ok btn
        okBtn=gtk.Button(_("Apply"))
        okBtn.set_size_request(IlUtil.btnW,IlUtil.btnH)
        okBtn.connect("button-press-event",self.onOkPressed)
        okAlign=gtk.Alignment(1,0.5,0,0)
        okAlign.add(okBtn)
        btnsBox.pack_start(okAlign,True,True)
        #cancel btn
        cancelBtn=gtk.Button(_("Cancel"))
        cancelBtn.set_size_request(IlUtil.btnW,IlUtil.btnH)
        cancelBtn.connect("button-press-event",self.onCancelPressed)
        cancelAlign=gtk.Alignment(1,0.5,0,0)
        cancelAlign.add(cancelBtn)
        btnsBox.pack_start(cancelAlign,False,True)
        #show all ui
        self.window.show_all()

