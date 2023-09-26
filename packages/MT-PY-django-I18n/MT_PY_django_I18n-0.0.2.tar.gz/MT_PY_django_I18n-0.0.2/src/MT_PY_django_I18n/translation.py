import os
import json
import polib
import gettext
from datetime import timezone
import datetime

# create mo file 
def create_mo_file(po_file_path, mo_file_path):
    gettext.install('messages', localedir=None)
    gettext.find('messages', localedir=None, all=True)
    with open(po_file_path, 'rb') as po_file:
        with open(mo_file_path, 'wb') as mo_file:
            mo_contents = gettext.GNUTranslations(po_file)
            mo_contents.write_mo(mo_file) 
# from django.conf import settings
# from django.core.management import call_command
# def create_mo_file(tran_list,proj_name):
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{proj_name}.settings')
#         # Iterate over the target languages and generate .mo files
#     for language in tran_list:
#         settings.LANGUAGE_CODE = language
#         call_command('compilemessages')


default_text=f'''


# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: {datetime.datetime.now(timezone.utc)}\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"Language: \n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"

'''
# create locale folder inside 

def create_translation_files(json_file,tran_list,proj_name):

    if not (os.path.exists("locale") and os.path.isdir("locale")):
        os.mkdir('locale')
        with open(json_file,"r",encoding="utf-8") as tran_data:
            data = json.load(tran_data)
            os.chdir('locale')
    # Read the json create folder by language code.

        for lang_code,trans in data.items():
            os.mkdir(lang_code)
            os.chdir(lang_code)
            os.mkdir('LC_MESSAGES')
            os.chdir('LC_MESSAGES')

           # file=open("messages.po","w")
            with open("messages.po","a+") as file:
                po=polib.POFile()
                file.writelines(default_text)

                
                
                
                for key,value in trans.items(): 
                    #problematic_string.decode('utf-8')
                    entry = polib.POEntry(msgid=key, msgstr=value)
                    po.append(entry)
                po.save("messages.po")
            file_path=os.getcwd()
            # create_mo_file(os.path.join(file_path,"messages.po"),os.path.join(file_path,"messages.mo"))
            # create_mo_file(tran_list,proj_name)
            os.chdir("..")
            os.chdir("..")
    


# create folder by name lang code
# create folder LC_MESSAGES create .mo and .po file if it is in django give django.po and django.mo else
# give messages.po and messages.mo
