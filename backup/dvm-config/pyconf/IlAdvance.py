#!/usr/bin/python
# Name: IlAdvance.py (Input Language - Advance Dialog)
# Desc: A dialog showing the advanced SCIM settings and the IM list,
#       triggered by the "Advanced" btn or the "Add/Remove Input Methods" in the Im combobox.
# Date: 2010.03.24 - 1st release
#       2010.06.17 - 2nd release, rewrite to separate functionality widgets to individual files
# Depend: 1.va-config.st2.0
#         2.bs-scim_simf
# Note: 1.Usage:
#         import IlAdvance
#         ...
#         def setAdvanceChange(self,result=True):
#         ...
#         def setImInfoDic(self,inputImDic):
#         ...
#         IlAdvance.DialogWidget(self,[current input language],[current keyboard],[current IM info dic],\
#                                [parent's window],[page type],[save mode])
#         ...
#
#       2.APIs:
#         (1)def setAdvanceChange(self,result=True):
#            Input:result(bool) - Ture if the settings are changed, otherwise False.
#            Output:None
#         (2)def setImInfoDic(self,inputImDic):
#            Input: inputImDic(dictionary) - send the IM Dictionary.
#            Output: None

#from std python
import gettext
import gobject
import pango
import os

#from pygtk
import pygtk
pygtk.require('2.0')
import gtk

#from config.st2.0
import Util
import Dialog

#from config.st2.0.input-lang
import IlUtil
import ssml
import simf

#---constant variables---

PanelSetupModule="panel-gtk-setup.so"

#treeview column
(
    IconCol,
    NameCol,
    EnableCol,
    IncCol,
    UuidCol
)=range(5)

#---class---

class DialogWidget:
    #[API needed by pyconf.Dialog]deal with restartx event(write config and restart x)
    def restartx(self,reponse):
        if reponse=="Yes":
            #restartx
            cmd="bbdock -x %s/X_quit" %Util.PATH
            os.system(cmd)
        else:
            #destroy RX and the advanced dialogs
            self.popup.dialog.destroy()

    def delete_event(self,widget,event=None,data=None):
        return False

    def destroy(self,widget,data=None):
        ssml.close()
        return False

    #when ok btn is pressed
    def onOkPressed(self,widget,data=None):
        #always send ImDic when pressing ok
        self.parent.setImInfoDic(self.curImInfoDic)
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
                self.parent.setAdvanceChange(True);
                self.window.destroy()
        else:
            self.window.destroy()

    #when cancel btn is pressed
    def onCancelPressed(self,widget,data=None):
        self.parent.setImInfoDic(self.curImInfoDic)
        self.window.destroy()

    #when expand btn is pressed
    def onExpPressed(self,widget,data=None):
        self.imTv.expand_all()

    #when collapse btn is pressed
    def onColPressed(self,widget,data=None):
        self.imTv.collapse_all()

    #when enable all btn is pressed
    def onEnAllPressed(self,widget,data=None):
        model=self.imTv.get_model()
        iter=model.get_iter_root()
        while iter!=None:
            model.set(iter,IncCol,False)
            model.set(iter,EnableCol,True)
            for i in range(model.iter_n_children(iter)):
                childIter=model.iter_nth_child(iter,i)
                enabledVal=model.get_value(childIter,EnableCol)
                if enabledVal==False:
                    model.set(childIter,EnableCol,True)
                    uuid=model.get_value(childIter,UuidCol)
                    self.curImInfoDic=IlUtil.setUuidWithMaxPri(uuid,self.curImInfoDic,self.curIl).copy()
            iter=model.iter_next(iter)

    #when disable all btn is pressed
    def onDisAllPressed(self,widget,data=None):
        model=self.imTv.get_model()
        iter=model.get_iter_root()
        while iter!=None:
            model.set(iter,IncCol,False)
            model.set(iter,EnableCol,False)
            for i in range(model.iter_n_children(iter)):
                childIter=model.iter_nth_child(iter,i)
                enabledVal=model.get_value(childIter,EnableCol)
                if enabledVal==True:
                    model.set(childIter,EnableCol,False)
                    uuid=model.get_value(childIter,UuidCol)
                    self.curImInfoDic=IlUtil.disableImWithUuid(uuid,self.curImInfoDic).copy()
            iter=model.iter_next(iter)

    #create im tree model
    def createImModel(self,langStr):
        #get data from simf and current scim config 
        imInfoDic=IlUtil.getImInfoDicWithLang(langStr,"all")
        for uuid in imInfoDic:
            if uuid in self.curImInfoDic:
                imInfoDic[uuid]=self.curImInfoDic[uuid]
            else:
                imInfoDic[uuid][IlUtil.InfoPri]=0
        #create language list
        langList=[]
        for uuid in imInfoDic:
            langList.append(imInfoDic[uuid][IlUtil.InfoLocale])
        langList=list(set(langList))
        langList.sort()
        #insert im in model
        model=gtk.TreeStore(gtk.gdk.Pixbuf,gobject.TYPE_STRING,gobject.TYPE_BOOLEAN,\
                            gobject.TYPE_BOOLEAN,gobject.TYPE_STRING)
        langImDic={}
        for lang in langList:
            iter=model.append(None)
            model.set(iter,
                IconCol,None,
                NameCol,_(IlUtil.convertLocaleToLang(lang)),
                EnableCol,True,
                IncCol,False,
                UuidCol,None)
            langInfoList=[]
            for uuid in imInfoDic:
                if imInfoDic[uuid][IlUtil.InfoLocale]==lang:
                    langInfoList.append(imInfoDic[uuid]);
            langImDic[lang]=langInfoList
            for imInfo in langImDic[lang]:
                childIter=model.append(iter)
                model.set(childIter,
                    IconCol,gtk.gdk.pixbuf_new_from_file_at_size(imInfo[IlUtil.InfoIcon],20,20),
                    NameCol,_(imInfo[IlUtil.InfoName]),
                    EnableCol,imInfo[IlUtil.InfoPri]>0,
                    IncCol,False,
                    UuidCol,imInfo[IlUtil.InfoUuid])
        return model
 
    def onEnableToggled(self,cell,path_str):
        model=self.imTv.get_model()
        iter=model.get_iter_from_string(path_str)
        toggleItem=model.get_value(iter,EnableCol)
        if model.iter_parent(iter)==None:
            self.imTv.expand_row(path_str,True)
            for i in range(model.iter_n_children(iter)):
                childIter=model.iter_nth_child(iter,i)
                model.set(childIter,EnableCol,not toggleItem)
                uuid=model.get_value(childIter,UuidCol)
                #set all child im 
                if toggleItem==True:
                    self.curImInfoDic=IlUtil.disableImWithUuid(uuid,self.curImInfoDic).copy()
                else:
                    self.curImInfoDic=IlUtil.setUuidWithMaxPri(uuid,self.curImInfoDic,self.curIl).copy()
        else:
            uuid=model.get_value(iter,UuidCol)
            if toggleItem==True:
                self.curImInfoDic=IlUtil.disableImWithUuid(uuid,self.curImInfoDic).copy()
            else:
                self.curImInfoDic=IlUtil.setUuidWithMaxPri(uuid,self.curImInfoDic,self.curIl).copy()
        model.set(iter,EnableCol,not toggleItem)
        self.updateIncState(iter)

    def updateIncState(self,inputIter=None):
        model=self.imTv.get_model()
        if inputIter==None:
            #all update
            iter=model.get_iter_root()
            while iter!=None:
                counter=0
                for i in range(model.iter_n_children(iter)):
                    childIter=model.iter_nth_child(iter,i)
                    enabledVal=model.get_value(childIter,EnableCol)
                    if enabledVal==True:
                        counter+=1
                childNum=model.iter_n_children(iter)
                if 0<counter<childNum:
                    model.set(iter,EnableCol,True)
                    model.set(iter,IncCol,True)
                elif counter==childNum:
                    model.set(iter,IncCol,False)
                    model.set(iter,EnableCol,True)
                else:
                    model.set(iter,IncCol,False)
                    model.set(iter,EnableCol,False)
                iter=model.iter_next(iter)
        else:
            iter=model.iter_parent(inputIter)
            if iter==None:
                #it is a lang
                iter=inputIter
            counter=0
            for i in range(model.iter_n_children(iter)):
                childIter=model.iter_nth_child(iter,i)
                enabledVal=model.get_value(childIter,EnableCol)
                if enabledVal==True:
                    counter+=1
            childNum=model.iter_n_children(iter)
            if 0<counter<childNum:
                model.set(iter,EnableCol,True)
                model.set(iter,IncCol,True)
            elif counter==childNum:
                model.set(iter,IncCol,False)
                model.set(iter,EnableCol,True)
            else:
                model.set(iter,IncCol,False)
                model.set(iter,EnableCol,False)

    def __init__(self,parent,inputIl,inputKb,inputImInfoDic={},\
                 parentWin=None,inputPage=IlUtil.AddRmImPage,inputSaveMode=IlUtil.NS):
        
        #class variables
        self.curIl=inputIl
        self.curKb=inputKb          #No use now, prepare for keyboard checking
        self.curImInfoDic={}
        self.parent=parent
        self.window=None
        self.saveMode=inputSaveMode
        self.imTv=None

        #---data initialize---

        if inputImInfoDic=={} or inputImInfoDic==None:
            self.curImInfoDic=IlUtil.getImInfoDicWithLang(inputIl).copy()
        else:
            self.curImInfoDic=inputImInfoDic.copy()

        #initialize ssml
        ssml.init(PanelSetupModule);

        #---ui initialize---

        #initiailize locale
        gettext.bindtextdomain(IlUtil.RcDomain,IlUtil.LocaleDir)
        gettext.textdomain(IlUtil.RcDomain)
        gettext.install(IlUtil.RcDomain,IlUtil.LocaleDir,unicode=1)

        #main window
        window=gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event",self.delete_event)
        window.connect("destroy",self.destroy)
        window.set_size_request(IlUtil.mainW,IlUtil.mainH)
        window.set_resizable(False)
        window.set_modal(True)
        window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        window.set_title(_("Advanced Input Language Settings"))
        window.set_keep_above(True)
        if parentWin!=None:
            window.set_transient_for(parentWin)
        if inputSaveMode==IlUtil.IS:
            window.set_decorated(False)
        self.window=window

        #main vbox
        mainBox=gtk.VBox(False,IlUtil.padW)
        mainBox.set_border_width(IlUtil.padW)
        self.window.add(mainBox)

        #--im notebook--
        imNotebook=gtk.Notebook()
        self.imNotebook=imNotebook
        mainBox.pack_start(self.imNotebook,True,True)

        #-add/remove input method page-
        addRmImBox=gtk.VBox(False,IlUtil.padW)
        addRmImBox.set_border_width(IlUtil.padW)
        addRmPageLb=gtk.Label(_("Add/Remove Input Method"))
        self.imNotebook.append_page(addRmImBox,addRmPageLb)

        #add/remove im label
        addRmLb=gtk.Label(_("The installed input method services:"))
        addRmLbAlign=gtk.Alignment(0,0,0,0)
        addRmLbAlign.add(addRmLb)
        addRmImBox.pack_start(addRmLbAlign,False,False)

        #add/remove im treeview
        sw=gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        addRmImBox.pack_start(sw,True,True)
        model=self.createImModel(inputIl)
        self.imTv=gtk.TreeView(model)
        self.imTv.set_rules_hint(True)
        #create name col
        column=gtk.TreeViewColumn()
        column.set_title(_("Name"))
        renderer=gtk.CellRendererPixbuf()
        column.pack_start(renderer,expand=False)
        column.add_attribute(renderer,'pixbuf',IconCol)
        renderer=gtk.CellRendererText()
        column.pack_start(renderer,expand=True)
        column.add_attribute(renderer,'text',NameCol)
        self.imTv.append_column(column)
        #create enable col
        renderer=gtk.CellRendererToggle();
        renderer.set_property("xalign",0.0)
        renderer.set_data("column",EnableCol)
        renderer.connect("toggled",self.onEnableToggled)
        column=gtk.TreeViewColumn(_("Enable"),renderer,active=EnableCol,inconsistent=IncCol)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(100)
        column.set_clickable(True)
        self.imTv.append_column(column)
        self.updateIncState()
        sw.add(self.imTv)

        #add/remove im btns
        addRmBtnsBox=gtk.HBox(False,IlUtil.padW)
        addRmBtnsBox.set_border_width(IlUtil.padW)
        addRmImBox.pack_start(addRmBtnsBox,False,False)

        expBtn=gtk.Button(_("Expand"))
        expBtn.set_size_request(IlUtil.btnW,IlUtil.btnH)
        expBtn.connect("button-press-event",self.onExpPressed)
        addRmBtnsBox.pack_start(expBtn,False,False)

        colBtn=gtk.Button(_("Collapse"))
        colBtn.set_size_request(IlUtil.btnW,IlUtil.btnH)
        colBtn.connect("button-press-event",self.onColPressed)
        addRmBtnsBox.pack_start(colBtn,False,False)

        enAllBtn=gtk.Button(_("Enable All"))
        enAllBtn.set_size_request(IlUtil.btnW,IlUtil.btnH)
        enAllBtn.connect("button-press-event",self.onEnAllPressed)
        addRmBtnsBox.pack_start(enAllBtn,False,False)

        disAllBtn=gtk.Button(_("Disable All"))
        disAllBtn.set_size_request(IlUtil.btnW,IlUtil.btnH)
        disAllBtn.connect("button-press-event",self.onDisAllPressed)
        addRmBtnsBox.pack_start(disAllBtn,False,False)

        #-toolbar page-
        self.setupWidget=ssml.getwidget()
        ssml.loadconfig()
        self.setupWidget.show()
        toolPageLb=gtk.Label(_("Toolbar"))
        self.imNotebook.append_page(self.setupWidget,toolPageLb)
        
        #--bottom btns hbox--
        btnsBox=gtk.HBox(False,IlUtil.padW*3)
        btnsBox.set_border_width(IlUtil.padW*3)
        bbAlign=gtk.Alignment(1,0,0,0)
        bbAlign.add(btnsBox)
        mainBox.pack_start(bbAlign,False,False)

        #ok btn
        okBtn=gtk.Button(_("Apply"))
        okBtn.set_size_request(IlUtil.btnW,IlUtil.btnH)
        okBtn.connect("button-press-event",self.onOkPressed)
        btnsBox.pack_start(okBtn)
        
        #cancel btn
        cancelBtn=gtk.Button(_("Cancel"))
        cancelBtn.set_size_request(IlUtil.btnW,IlUtil.btnH)
        cancelBtn.connect("button-press-event",self.onCancelPressed)
        btnsBox.pack_start(cancelBtn)

        #show all ui
        self.window.show_all()

        #XXX:set current page must be called at the last,
        #    because it only works when all widgets in notebook are shown.
        self.imNotebook.set_current_page(inputPage)

