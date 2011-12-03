#!/usr/bin/python
# Name: Il.py (Input Language)
# Desc: The main widget using in the Input Language Configure Panel
# Date: 2010.03.24 - 1st release
#       2010.06.18 - 2nd release, rewrite to separate functionality widgets to individual files
# Depend: 1.va-config.st2.0
#         2.bs-scim_simf
# Note: 1.Widgets in the Input Language Configure Panel:
#         Il.MainWidget - the Input Language main widget, include Il,Kb,Im combobox.
#         IlAbout.Dialog - a dialog including the about info, triggered by the "About" btn.
#         IlDetail.Dialog - a dialog showing the detail settings in some IMs
#                           (Chewing, Smart-Pinyin, Anthy, Korean and Thai),
#                           triggered by the "..." btn.
#         IlAdvance.Dialog - a dialog showing the advanced SCIM settings and the IM list,
#                            triggered by the "Advanced" btn or the "Add/Remove input method" in the Im combobox.
#
#       2.Usage:
#         import Il
#         ...
#         def closePanel(self):
#             ...
#         ...
#         IlMainWidget=Il.MainWidget(self,[parent's window],[input widget width],[save mode])
#         returnedWidget=IlMainWidget.getWidget()
#         ...
#         IlMainWidget.onOkPressed()
#         ...
#         IlMainWidget.onCancelPressed()
#         ...
#
#       3.APIs:
#         (1)IlMainWidget.getWidget() - get the main widget of the Input Language Configure Panel
#            Input:None
#            Output:(gtk.Alignment) - the main widget of the Input Language Configure Panel
#         (2)IlMainWidget.onOkPressed() - receive a "ok btn pressed" event from parent
#            (usually using in the Normal Save mode)
#            Input:None
#            Output:None
#         (3)IlMainWidget.onCancelPressed() - receive a "cancel btn pressed" event from parent 
#            (usually using in the Normal Save mode)
#            Input:None
#            Output:None
#         (4)IlMainWidget.releaseSsmlModules() - release all ssml-type modules
#            - It should be called when the configure panel is closed.
#            Input:None
#            Output:None
#         (5)def closePanel(self) - send a "close panel" event to parent, for closing the panel.
#            Input:None
#            Output:None

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
import Util
import VAEnv
import Dialog

#from config.st2.0.input-lang
import IlUtil
import IlAdvance
import IlDetail

#---constant variables---

widgetW=400     #main widget width
sideW=50        #side width (from frame to combobox side)

#input method combobox columns
(
    LangCol,
    IconCol,
    NameCol,
    FunCol
)=range(4)

#---class---
class MainWidget:
    #[API]receive the "ok btn pressed" event from parent.
    def onOkPressed(self):
        self.saveNRXconfig()
        if self.confirmRX():
            #save RestartX configures after confirmRX
            self.saveRXconfig()
            #trigger the "Restart X" Dialog
            self.popup=Dialog.dlgRestart(self)
            self.popup.dialog.set_title(_("Input Language"))
        else:
            if self.saveMode==IlUtil.NS:
                #if the save mode is Normal Save, close panel immediately
                self.parent.closePanel()

    #[API]receive the "cancel btn pressed" event from parent.
    def onCancelPressed(self):
        self.parent.closePanel()

    #[API]get the main widget of the Input Language Configure Panel
    def getWidget(self):
        return self.widget

    #[API needed by IlDetail.Dialog]set the query change
    def setDetailChange(self,inputUuid,result=True):
        self.detailChange[inputUuid]=result

    #[API needed by IlAdvance.Dialog]set the query change
    def setAdvanceChange(self,result=True):
        self.advanceChange=result

    #[API needed by IlAdvance.Dialog]set the current ImDic
    def setImInfoDic(self,inputImInfoDic=None):
        if inputImInfoDic=={} or inputImInfoDic==None:
            #1.change the default IM to English
            self.curImInfoDic=IlUtil.setUuidWithMaxPri(IlUtil.EnglishImUuid,{},self.curIl)
            #2.disable IM
            self.setEnableImAndChangeUi(False)
        else:
            self.curImInfoDic=inputImInfoDic.copy()
        self.setupImComboBox()

    #[API needed by Dialog]deal with restartx event(write config and restart x)
    def restartx(self,reponse):
        if reponse=="Yes":
            #1.restartx
            cmd="bbdock -x %s/X_quit" %Util.PATH
            os.system(cmd)
        else:
            self.popup.dialog.destroy()
            if self.saveMode==IlUtil.NS:
                #if the save mode is Normal Save, close panel immediately
                self.parent.closePanel()

    #when input language combobox is changed 
    def onIlComboBoxChanged(self,widget,data=None):
        #to avoid onOkPressed being triggered before all configures are ready,
        #set saveMode to IlUtil.DIS temporarily.
        disableInstantSave=False
        if self.saveMode==IlUtil.IS:
            disableInstantSave=True
            self.saveMode=IlUtil.DIS
        #get selected input lang
        self.curIl=self.ilList[self.ilCb.get_active()]
        self.changeKbAndImWithLang()
        #rollback saveMode to IlUtil.IS
        if disableInstantSave:
            self.saveMode=IlUtil.IS
            self.onOkPressed()

    #when keyboard combobox is changed 
    def onKbComboBoxChanged(self,widget,data=None):
        self.curKb=self.kbList[self.kbCb.get_active()]
        if self.saveMode==IlUtil.IS:
            self.onOkPressed()

    #when im check btn is toggled
    def onImCheckBtnToggled(self,widget,data=None):
        if widget.get_active():
            self.curEnableIm=True
            self.imCb.set_sensitive(True)
            self.advBtn.set_sensitive(True)
            self.onImComboBoxChanged(self.imCb)
        else:
            self.curEnableIm=False
            self.imCb.set_sensitive(False)
            self.detailBtn.set_sensitive(False)
            self.advBtn.set_sensitive(False)
        if self.saveMode==IlUtil.IS:
            self.onOkPressed()

    #when im combobox is changed 
    def onImComboBoxChanged(self,widget,data=None):
        selectedIndex=self.imCb.get_active()
        if selectedIndex==-1 or self.imCbIndexDic==None:
            return
        imCbData=self.imCbIndexDic[selectedIndex]
        if imCbData=="LangLabel":
            nextIndex=self.imCb.get_active()+1
            self.imCb.set_active(nextIndex);
            self.onImComboBoxChanged(self.imCb);
        if imCbData=="AddRemoveBtn":
            #trigger the Add/Remove Widget
            IlAdvance.DialogWidget(self,self.curIl,self.curKb,self.curImInfoDic,\
                                   self.window,IlUtil.AddRmImPage,self.saveMode)
        if type(imCbData) is ListType:
            #check if detail btn is available
            if imCbData[IlUtil.InfoUuid] in IlUtil.SetupModuleDic:
                self.detailBtn.set_sensitive(True)
                if self.detailHandlerId!=None:
                    self.detailBtn.disconnect(self.detailHandlerId)
                self.detailHandlerId=\
                self.detailBtn.connect("button-release-event",self.onDetailBtnPressed,imCbData[IlUtil.InfoUuid])
            else:
                self.detailBtn.set_sensitive(False)
            #change it to max pri im
            self.curImInfoDic=\
            IlUtil.setUuidWithMaxPri(imCbData[IlUtil.InfoUuid],self.curImInfoDic.copy(),self.curIl).copy()
        if self.saveMode==IlUtil.IS:
            #save im data immediately
            self.saveNRXconfig()

    #when im detail btn is pressed
    def onDetailBtnPressed(self,widget,data,uuid):
        IlDetail.DialogWidget(self,uuid,self.window,self.saveMode)

    #when advance btn is pressed
    def onAdvBtnPressed(self,widget,data=None):
        IlAdvance.DialogWidget(self,self.curIl,self.curKb,self.curImInfoDic,\
                               self.window,IlUtil.ToolbarPage,self.saveMode)

    #change keyboard and input method combobox when the language is changed.
    def changeKbAndImWithLang(self):
        #setup keyboard
        self.curKb=IlUtil.getDefaultKbWithLang(self.curIl)
        self.kbCb.set_active(self.kbList.index(self.curKb))
        #setup input method
        self.curImInfoDic=IlUtil.getImInfoDicWithLang(self.curIl).copy()
        self.setupImComboBox()
        #check if it need disable/enable im
        if self.curImInfoDic.keys()==[IlUtil.EnglishImUuid]:
            self.setEnableImAndChangeUi(False)
        else:
            self.setEnableImAndChangeUi(True)

    #setup im combobox
    def setupImComboBox(self):
        #clear data
        self.imLs.clear()
        self.imCbIndexDic={}
        #get max priority im 
        maxPriUuid=IlUtil.getUuidWithMaxPri(self.curImInfoDic)
        #create locale list
        localeList=[]#localeList=[locale1,locale2,...]
        for uuid in self.curImInfoDic:
            localeList.append(self.curImInfoDic[uuid][IlUtil.InfoLocale])
        localeList=list(set(localeList))
        localeList.sort()
        #create im combo box
        localeInfoDic={}#localeInfoDic={locale:im_info_list}
        counter=0
        for lang in localeList:
            localeInfoList=[]#localeInfoList=[im_info1,im_info2,...]
            for uuid in self.curImInfoDic:
                if self.curImInfoDic[uuid][IlUtil.InfoLocale]==lang:
                    localeInfoList.append(self.curImInfoDic[uuid]);
            localeInfoDic[lang]=localeInfoList
            self.imLs.append((_(IlUtil.convertLocaleToLang(lang)),None,None,None))
            self.imCbIndexDic[counter]="LangLabel"
            counter+=1
            for imInfo in localeInfoDic[lang]:
                self.imLs.append(("   ",gtk.gdk.pixbuf_new_from_file_at_size(imInfo[IlUtil.InfoIcon],20,20),\
                                _(imInfo[IlUtil.InfoName]),""))
                self.imCbIndexDic[counter]=imInfo
                if imInfo[IlUtil.InfoUuid]==maxPriUuid:
                    self.imCb.set_active(counter);
                counter+=1
        self.imLs.append((None,None,None,_("Add/Remove...")))
        self.imCbIndexDic[counter]="AddRemoveBtn"

    #set the current EnableIm and change the Ui display
    def setEnableImAndChangeUi(self,result=True):
        if result:
            self.imCBtn.set_active(True)
        else:
            self.imCBtn.set_active(False)
        self.imCBtn.toggled()

    #confirm if it needs restartx
    def confirmRX(self):
        #check settings in all detail dialogs
        detailChange=False
        for uuid in IlUtil.SetupModuleDic.keys():
            if self.detailChange[uuid]==True:
                detailChange=True
                break
        xkbenable=os.environ.get("DI_DEF_KB_XKB","no")
        if xkbenable=="yes":
            #if xkb is enabled, only EnableIm and other scim settings which need to restartx
            if self.oriEnableIm!=self.curEnableIm or detailChange or self.advanceChange:
                return True
        else:
            #check input language, keyboard, EnableIm and other scim settings which need to restartx
            if self.oriIl!=self.curIl or self.oriKb!=self.curKb or self.oriEnableIm!=self.curEnableIm or \
            detailChange or self.advanceChange:
                return True
        return False

    #save the Non-RestartX configures
    def saveNRXconfig(self):
        #Only the modification of ImList needn't restartx, other configures need to restartx.
        #compare the imInfoDic data(no need to restartx)
        oriSortedUuid=[]
        oriPriList=[self.oriImInfoDic[uuid][4] for uuid in self.oriImInfoDic.keys()]
        oriPriList.sort()
        for pri in oriPriList:
            for uuid in self.oriImInfoDic.keys():
                if self.oriImInfoDic[uuid][4]==pri:
                    oriSortedUuid.append(uuid)
                    break
        curSortedUuid=[]
        curPriList=[self.curImInfoDic[uuid][4] for uuid in self.curImInfoDic.keys()]
        curPriList.sort()
        for pri in curPriList:
            for uuid in self.curImInfoDic.keys():
                if self.curImInfoDic[uuid][4]==pri:
                    curSortedUuid.append(uuid)
                    break
        if oriSortedUuid!=curSortedUuid:
            IlUtil.writeImInfo(oriSortedUuid,curSortedUuid,self.curIl)
        #if use XKB, also save the current input language and keyboard
        xkbenable=os.environ.get("DI_DEF_KB_XKB","no")
        if xkbenable=="yes":
            if self.curIl!=self.oriIl:
                Util.set_env_param("INPUTLANG",self.curIl)
            if self.curKb!=self.oriKb:
                Util.set_env_param("KEYBOARD",self.curKb)
                cmd="/bin/setuserkeyboard"
                os.system(cmd)
        if self.saveMode==IlUtil.IS:
            #restore configure data
            self.oriImInfoDic=self.curImInfoDic.copy()

    #save the RestartX configures
    def saveRXconfig(self):
        xkbenable=os.environ.get("DI_DEF_KB_XKB","no")
        if xkbenable!="yes":
            Util.set_env_param("INPUTLANG",self.curIl)
            Util.set_env_param("KEYBOARD",self.curKb)
        if self.curEnableIm:
            Util.set_env_param("NO_IM","no")
        else:
            Util.set_env_param("NO_IM","yes")
        if self.saveMode==IlUtil.IS:
            self.storeCurToOri()

    #store the current settings to the original settings
    def storeCurToOri(self):
        self.oriIl=self.curIl
        self.oriKb=self.curKb
        self.oriEnableIm=self.curEnableIm
        self.oriImInfoDic=self.curImInfoDic.copy()

    #initiailize
    def __init__(self,parent,parentWin=None,inputWidgetW=widgetW,inputSaveMode=IlUtil.NS):

        #class variable(just for comments)
        self.parent=parent          #the parent(class)
        self.window=parentWin       #the window which include MainWidget(gtk.Window)
        cbW=inputWidgetW-2*sideW    #combobox width
        self.saveMode=inputSaveMode #the current save mode(IlUtil.NS/IlUtil.IS)
        self.widget=None            #the main widget for return(gtk.Alignment)

        self.ilList=[]              #input language list([il1,il2,...])
        self.kbList=[]              #keyboard list([kb1,kb2,...])

        self.oriIl=None             #original input language(string)
        self.oriKb=None             #original keyboard(string)
        self.oriEnableIm=None       #original im flag(true/false)
        self.oriImInfoDic={}        #original IM info dictionary({uuid:ImInfo})

        self.curIl=None             #current input language(string)
        self.curKb=None             #current keyboard(string)
        self.curEnableIm=None       #current im flag(true/false)
        self.curImInfoDic={}        #current IM info dictionary({uuid:ImInfo})

        self.ilCb=None              #input language combobox(gtk.ComboBox)
        self.kbCb=None              #keyboard combobox(gtk.ComboBox)
        self.imCBtn=None            #input method check btn(gtk.CheckButton)
        self.imLs=None              #input method listStore(gtk.ListStore)
        self.imCb=None              #input method combobox(gtk.ComboBox)
        self.imCbIndexDic={}        #input method combobox index directory
                                    #=index:im info(list)/"LangLabel"(string)/"AddRemoveBtn"(string)
        self.detailBtn=None         #input method detail btn(gtk.Button)
        self.detailHandlerId=None   #detail btn press handler
        self.advBtn=None            #advance btn(gtk.Button)

        self.detailChange=dict([(value,False) for value in IlUtil.SetupModuleDic.keys()])
        self.advanceChange=False
        
        #-----data initiailize-----

        #get env variables
        self.ilList=IlUtil.getInputLangList()
        self.kbList=IlUtil.getKeyboardList()
        self.curIl=Util.get_env_param('INPUTLANG')
        if self.curIl==None or self.curIl=="":
            self.curIl=Util.get_env_param('LANGNAME')
            Util.set_env_param('INPUTLANG',self.curIl)
        self.curKb=Util.get_env_param('KEYBOARD')
        if self.curKb not in self.kbList:
            if self.curKb=="U.S.English":
                self.curKb="English U.S."
                Util.set_env_param("KEYBOARD",self.curKb)
            elif self.curKb=="United Kingdom":
                self.curKb="English U.K."
                Util.set_env_param("KEYBOARD",self.curKb)
            elif self.curKb=="Arabic(001)":
                self.curKb="Arabic (001)"
                Util.set_env_param("KEYBOARD",self.curKb)
            elif self.curKb=="Arabic(002)":
                self.curKb="Arabic (002)"
                Util.set_env_param("KEYBOARD",self.curKb)
            elif self.curKb=="Czech(QWERTY)":
                self.curKb="Czech (QWERTY)"
                Util.set_env_param("KEYBOARD",self.curKb)
            elif self.curKb=="Polish(programmers)":
                self.curKb="Polish (programmers)"
                Util.set_env_param("KEYBOARD",self.curKb)
            elif self.curKb=="Portuguese(Brazilian ABNT)":
                self.curKb="Portuguese (Brazilian ABNT)"
                Util.set_env_param("KEYBOARD",self.curKb)
            elif self.curKb=="Slovak(QWERTY)":
                self.curKb="Slovak (QWERTY)"
                Util.set_env_param("KEYBOARD",self.curKb)
            else:
                pass
        curNoIm=Util.get_env_param('NO_IM')
        if curNoIm=="" or curNoIm=="no":
            self.curEnableIm=True
        else:
            self.curEnableIm=False
        self.curImInfoDic=IlUtil.getImInfoDicWithLang(self.curIl).copy()

        #store initial data
        self.storeCurToOri();

        #-----ui initiailize-----
        
        #initiailize locale
        gettext.bindtextdomain(IlUtil.RcDomain,IlUtil.LocaleDir)
        gettext.textdomain(IlUtil.RcDomain)
        gettext.install(IlUtil.RcDomain,IlUtil.LocaleDir,unicode=1)

        #---mid area---

        #create ilBox and the return widget
        ilBox=gtk.VBox(False,IlUtil.padW*2)
        ilBox.set_size_request(inputWidgetW,-1)
        ilAlign=gtk.Alignment(0.5,0.5,0,0)
        ilAlign.add(ilBox)
        self.widget=ilAlign

        #create langSelect set
        langSelectBox=gtk.VBox(False,IlUtil.padW*2)
        langSelectBox.set_size_request(cbW,-1)
        langSelectBoxAlign=gtk.Alignment(0.5,0.5,0,0)
        langSelectBoxAlign.add(langSelectBox)
        ilBox.pack_start(langSelectBoxAlign,False,True)

        langSelectLb=gtk.Label(_("Input Language:"))
        langSelectLbAlign=gtk.Alignment(0,0.8,0,0)
        langSelectLbAlign.add(langSelectLb)
        langSelectBox.pack_start(langSelectLbAlign,False,True)

        ilCb=gtk.combo_box_new_text()
        for il in self.ilList:
            ilCb.append_text(_(il))
        if self.curIl not in self.ilList:
            #if previous setting not in list, set English
            if "English" in self.ilList:
                i=self.ilList.index("English")
                ilCb.set_active(i)
            else:
                ilCb.set_active(0)
        else:
            i=self.ilList.index(self.curIl)
            ilCb.set_active(i)
        ilCb.connect("changed",self.onIlComboBoxChanged)
        langSelectBox.pack_start(ilCb,True,True)
        self.ilCb=ilCb

        #create kbAndIm set
        kbAndImFrame=gtk.Frame()
        kbAndImFrame.set_shadow_type(gtk.SHADOW_OUT)
        ilBox.pack_start(kbAndImFrame,True,True)
        kbAndImBox=gtk.VBox(True,IlUtil.padW)
        kbAndImBox.set_border_width(IlUtil.padW*2)
        kbAndImBox.set_size_request(cbW+(IlUtil.padW*2)*2,-1)
        kbAndImBoxAlign=gtk.Alignment(0.5,0.5,0,0)
        kbAndImBoxAlign.add(kbAndImBox)
        kbAndImFrame.add(kbAndImBoxAlign)

        #create keyboardSelect set
        kbLb=gtk.Label(_("Keyboard:"))
        kbLbAlign=gtk.Alignment(0,0.8,0,0)
        kbLbAlign.add(kbLb)
        kbAndImBox.pack_start(kbLbAlign,False,True)
        kbCb=gtk.combo_box_new_text()
        kbCb.connect("changed",self.onKbComboBoxChanged)
        for kb in self.kbList:
            kbCb.append_text(_(kb))
        kbAndImBox.pack_start(kbCb,False,True)
        self.kbCb=kbCb
        #setup keyboard
        self.kbCb.set_active(self.kbList.index(self.curKb))

        #create imSelect set
        imCBtn=gtk.CheckButton(_("Input Method:"))
        imCBtn.connect("toggled",self.onImCheckBtnToggled)
        self.imCBtn=imCBtn
        imLbAlign=gtk.Alignment(0,0.8,0,0)
        imLbAlign.add(imCBtn)
        kbAndImBox.pack_start(imLbAlign,False,True)

        imFunBox=gtk.HBox(False,IlUtil.padW)
        kbAndImBox.pack_start(imFunBox,False,True)

        imLs=gtk.ListStore(gobject.TYPE_STRING,gtk.gdk.Pixbuf,\
                            gobject.TYPE_STRING,gobject.TYPE_STRING)
        self.imLs=imLs
        imCb=gtk.ComboBox(imLs)
        imCb.connect("changed",self.onImComboBoxChanged)
        titleCell=gtk.CellRendererText()
        #titleCell.set_properties(scale_set=True,scale=0.9)
        titleCell.set_property("scale_set",True)
        titleCell.set_property("scale",0.9)
        iconCell=gtk.CellRendererPixbuf()
        imnameCell=gtk.CellRendererText()
        actionCell=gtk.CellRendererText()
        #actionCell.set_properties(scale_set=True,scale=0.9,\
        #underline_set=True,underline=pango.UNDERLINE_LOW)
        actionCell.set_property("scale_set",True)
        actionCell.set_property("scale",0.9)
        actionCell.set_property("underline_set",True)
        actionCell.set_property("underline",pango.UNDERLINE_LOW)
        imCb.pack_start(titleCell,False)
        imCb.pack_start(iconCell,False)
        imCb.pack_start(imnameCell,True)
        imCb.pack_start(actionCell,False)
        imCb.add_attribute(titleCell,'text',LangCol)
        imCb.add_attribute(iconCell,'pixbuf',IconCol)
        imCb.add_attribute(imnameCell,'text',NameCol)
        imCb.add_attribute(actionCell,'text',FunCol)
        imFunBox.pack_start(imCb,True,True)
        self.imCb=imCb

        detailBtn=gtk.Button(_("..."))
        detailBtn.set_sensitive(False)
        imFunBox.pack_start(detailBtn,False,False)
        self.detailBtn=detailBtn

        #create advance btn
        advBtn=gtk.Button(_("Advanced"))
        advBtn.set_size_request(IlUtil.btnW,IlUtil.btnH)
        advBtn.connect("button-press-event",self.onAdvBtnPressed)
        advBtnAlign=gtk.Alignment(1,0.5,0,0)
        advBtnAlign.add(advBtn)
        kbAndImBox.pack_start(advBtnAlign,False,True)
        self.advBtn=advBtn

        #setup input method
        self.setupImComboBox()

        #setup disable/enable im
        self.setEnableImAndChangeUi(self.curEnableIm)

