#!/usr/bin/python
# Name: runInputLang.py
# Desc: run Input Language Configure Panel
# Date: 2010.03.24
#       2010.05.25 - separate window and main widget
#       2010.06.18 - support new IL widget
# Note:
# Depend: 1.va-config.st2.0
#         2.bs-scim_simf

#from std python
import gettext
import gobject
import pango
import os
from types import *

#from pygtk
import pygtk
pygtk.require('2.0')
import gtk

#from config.st2.0
import pyconf.Util
import pyconf.VAEnv

#from config.st2.0.input-lang
import pyconf.Il
import pyconf.IlUtil
import pyconf.IlAbout

#---constant variables---

midH=pyconf.IlUtil.mainH-pyconf.IlUtil.topH-pyconf.IlUtil.botH #middle area height
sideW=60 #side width(from window side to frame)
inputLangW=pyconf.IlUtil.mainW-2*sideW #input language set width

#---class---

#         def closePanel(self):
#             IlMainWidget.releaseSsmlModules()

class runInputLang:
    #[API needed by pyconf.Il]
    def closePanel(self):
        self.window.destroy()

    def delete_event(self,widget,event,data=None):
        return False

    def destroy(self,widget=None,data=None):
        gtk.main_quit()

    #when about btn is pressed
    def onAboutPressed(self,widget,data=None):
        pyconf.IlAbout.Dialog(self.window)

    #when ok btn is pressed
    def onOkPressed(self,widget,data=None):
        self.IlMainWidget.onOkPressed()

    #when cancel btn is pressed
    def onCancelPressed(self,widget,data=None):
        self.IlMainWidget.onCancelPressed()

    #initiailize
    def __init__(self):
        #class variable(just for comments)
        self.IlMainWidget=None  #the MainWidget from InputLang(MainWidget class)
        self.window=None        #main window(gtk.Window)

        #-----ui initiailize-----
        
        #initiailize locale
        gettext.bindtextdomain(pyconf.IlUtil.RcDomain,pyconf.IlUtil.LocaleDir)
        gettext.textdomain(pyconf.IlUtil.RcDomain)
        gettext.install(pyconf.IlUtil.RcDomain,pyconf.IlUtil.LocaleDir,unicode=1)

        #create window
        window=gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event",self.delete_event)
        window.connect("destroy",self.destroy)
        window.set_size_request(pyconf.IlUtil.mainW,pyconf.IlUtil.mainH)
        window.set_resizable(False)
        window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        window.set_title(_("Input Language"))
        self.window=window

        #create main box
        mainBox=gtk.VBox(False)
        window.add(mainBox)

        #---top area---

        #create top title
        insLo=gtk.Layout()
        insLo.set_size_request(pyconf.IlUtil.mainW,pyconf.IlUtil.topH)
        mainBox.pack_start(insLo,False,False)
        labelIns=gtk.Label(_("Please select your input language and input method."))
        insLo.put(labelIns,sideW,pyconf.IlUtil.topH/2)

        #create sepaarator
        sepTop=gtk.HSeparator()
        sepTop.set_size_request(pyconf.IlUtil.mainW,pyconf.IlUtil.sepW)
        mainBox.pack_start(sepTop,False,False)

        #---mid area---

        #get widget from InputLang
        self.IlMainWidget=pyconf.Il.MainWidget(self,self.window,inputLangW)
        mainBox.pack_start(self.IlMainWidget.getWidget(),True,True)

        #create separator
        sepBot=gtk.HSeparator()
        sepBot.set_size_request(pyconf.IlUtil.mainW,pyconf.IlUtil.sepW)
        mainBox.pack_start(sepBot,False,False)
        
        #---bottom area---

        #create buttons box
        btnsBox=gtk.HBox(False,pyconf.IlUtil.padW*3)
        btnsBox.set_size_request(pyconf.IlUtil.mainW,pyconf.IlUtil.botH)
        btnsBox.set_border_width(pyconf.IlUtil.padW*3)
        mainBox.pack_start(btnsBox,False,False)

        #about btn
        aboutBtn=gtk.Button(_("About"))
        aboutBtn.set_size_request(pyconf.IlUtil.btnW,pyconf.IlUtil.btnH)
        aboutBtn.connect("button-press-event",self.onAboutPressed)
        aboutAlign=gtk.Alignment(0,0.5,0,0)
        aboutAlign.add(aboutBtn)
        btnsBox.pack_start(aboutAlign,False,True)

        #ok btn
        okBtn=gtk.Button(_("OK"))
        okBtn.set_size_request(pyconf.IlUtil.btnW,pyconf.IlUtil.btnH)
        okBtn.connect("button-press-event",self.onOkPressed)
        okAlign=gtk.Alignment(1,0.5,0,0)
        okAlign.add(okBtn)
        btnsBox.pack_start(okAlign,True,True)

        #cancel btn
        cancelBtn=gtk.Button(_("Cancel"))
        cancelBtn.set_size_request(pyconf.IlUtil.btnW,pyconf.IlUtil.btnH)
        cancelBtn.connect("button-press-event",self.onCancelPressed)
        cancelAlign=gtk.Alignment(1,0.5,0,0)
        cancelAlign.add(cancelBtn)
        btnsBox.pack_start(cancelAlign,False,True)

        # show all ui
        self.window.show_all()

    def main(self): # The main, all Pygtk applications must have this function
        gtk.main()

# Run program
if __name__=="__main__":
    dvm=runInputLang()
    dvm.main()
