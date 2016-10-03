#!/usr/bin/env python

##########################################################
#
#            Soupy Paste WX
#
#      Soupy Paste is a tiny utility to create BeautifulSoup code by using your clipboard.
#   Go to a site and copy the smallest excerpt that starts with unique open html/xml tags and run
#   utility to get the bs4 code. This is the non-terminal version.
#
#
#   @author : jbsilva
#
##########################################################


import wx
from bs4 import BeautifulSoup

MENU_FILE_EXIT = wx.NewId()
DRAG_SOURCE    = wx.NewId()

class SoupExtractor:
    tag_attribs=['class','id']
    tabs_or_spaces='    '
    def get_tags(self,text):
        tag_text=[]
        for curr in text.split('<'):
            if '>' in curr:
                out_tag=curr.split('>')[0].split()[0]
                if not '/' in out_tag:
                    tag_text.append(out_tag)
        return tag_text

    def get_soup(self,text):
        soup = BeautifulSoup(text,"html.parser")
        tag_list=self.get_tags(text);
        tags_detailed=[]; tag_now=None
        for tag_curr in tag_list:
            if len(tags_detailed) < 1:
                curr_set = soup.find_all(tag_curr)
            else:
                curr_set = tag_now.find_all(tag_curr)
            tag_now=curr_set[0]
            tag_info={'tag':tag_curr}
            for attr in self.tag_attribs:
                if tag_now.has_attr(attr):
                    attr_info=tag_now[attr]
                    if 'list' in str(type(attr_info)):
                        tag_info[attr]=str( ' '.join(attr_info) )
                    else:
                        tag_info[attr] = str( attr_info )
            tags_detailed.append(tag_info)
        code_text=self.convert_details_to_code(tags_detailed)
        return code_text

    def convert_details_to_code(self, tag_details ):
        code_text=''
        code_text = code_text+"soup = BeautifulSoup(text,\"html.parser\")"+'\n\n'
        code_text = code_text + "text_out=''"+'\n'
        code_text = code_text +"for ind in range("+str(len(tag_details))+"):\n"
        for ind in range(len(tag_details)):
            if ind==0:
                code_text = code_text +self.tabs_or_spaces+"if ind == 0 :"+'\n'
                curr_line="curr_tag=soup.find_all('"+str(tag_details[ind]['tag'])+"'"
            else:
                curr_line="curr_tag=curr_tag.find_all('"+str(tag_details[ind]['tag'])+"'"
            for tag_inf in tag_details[ind]:
                if tag_inf != 'tag':
                    if not ':' in curr_line:
                        curr_line=curr_line+",{"
                    curr_line = curr_line + "'"+ tag_inf+"':"+"'"+tag_details[ind][tag_inf]+"',"
            if ':' in curr_line:
                curr_line=curr_line[:-1]+"}"
            curr_line = curr_line + ')[0];'
            if ind==0:
                code_text = code_text +2*self.tabs_or_spaces+curr_line+'\n'
            else:
                code_text = code_text +self.tabs_or_spaces+"elif ind =="+str(ind)+':'+'\n'
                code_text = code_text +2*self.tabs_or_spaces+curr_line+'\n'
            if ind+1 == len(tag_details):
                code_text = code_text +2*self.tabs_or_spaces+"text_out = curr_tag.text"+'\n'
        return code_text

class MainWindow(wx.Frame):
    text_to_code=None
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent, wx.ID_ANY, title, size = (750,600), style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)

        self.SetBackgroundColour(wx.WHITE)
        # Setup soup helper
        self.text_to_code=SoupExtractor()

        # setup menu bar
        menuBar = wx.MenuBar()
        menu1 = wx.Menu()
        menu1.Append(MENU_FILE_EXIT, "Exit", "Quit Soupy Paste")
        menuBar.Append(menu1, "&File")
        self.SetMenuBar(menuBar)
        wx.EVT_MENU(self, MENU_FILE_EXIT, self.CloseWindow)

        # setup dragdrop box
        self.text = wx.TextCtrl(self, DRAG_SOURCE, "", pos=(0,0), size=(750,200), style = wx.TE_MULTILINE|wx.HSCROLL)

        wx.EVT_RIGHT_DOWN(self.text, self.OnDragInit)

        # add buttons
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL); self.buttons = []

        # first row of buttons
        self.buttons.append(wx.Button(self, -1, "Paste "))
        self.sizer2.Add(self.buttons[0], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.GetPastedText,self.buttons[0])

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.text, 1, wx.EXPAND)
        self.sizer.Add(self.sizer2, 0, wx.EXPAND)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()

    def GetPastedText(self,event):
        if not wx.TheClipboard.IsOpened():
            wx.TheClipboard.Open();
            do = wx.TextDataObject()
            success = wx.TheClipboard.GetData(do)
            wx.TheClipboard.Close()
            if success:
                text_excerpt = do.GetText()
                code_text=self.text_to_code.get_soup(text_excerpt)
                self.text.SetValue(code_text)
                print code_text

            else:
                self.text.SetValue("There is no data in the clipboard in the required format")

    def CloseWindow(self, event):
        self.Close()

    def OnDragInit(self, event):
        tdo = wx.PyTextDataObject(self.text.GetStringSelection())
        tds = wx.DropSource(self.text)
        tds.SetData(tdo)
        tds.DoDragDrop(True)

class SoupyPasteWx(wx.App):
    def OnInit(self):
        frame = MainWindow(None, -1, "Soupy Paste - Press Button To Make Soup Excerpt")
        self.SetTopWindow(frame)
        return True

# main loop
app = SoupyPasteWx(0)
app.MainLoop()