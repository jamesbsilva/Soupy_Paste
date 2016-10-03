#!/usr/bin/env python

##########################################################
#
#            Soupy Paste
#
#      Soupy Paste is a tiny utility to create BeautifulSoup code by using your clipboard.
#   Go to a site and copy the smallest excerpt that starts with unique open html/xml tags and run
#   utility to get the bs4 code. This is the terminal version
#
#
#   @author : jbsilva
#
##########################################################


import pyperclip
from bs4 import BeautifulSoup

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

soupy_help=SoupExtractor()
text_in=pyperclip.paste()
code_text=soupy_help.get_soup(text_in)

print "---------Python----BeautifulSoup----Code-------------------"
print code_text
print "-----------------------------------------------------------"
