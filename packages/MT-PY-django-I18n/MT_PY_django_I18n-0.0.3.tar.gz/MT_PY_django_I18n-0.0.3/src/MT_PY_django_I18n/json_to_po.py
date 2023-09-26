import os
import json
import django
from django.core.management import call_command
from django.conf import settings
import locale

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog.settings')
# django.setup()

def custom_compile_messages(lang,proj_name):

    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{proj_name}.settings')

    # Your target languages for which you want to generate .mo files
    target_languages = lang  # ['fr', 'de', 'es']  # Add your desired languages here

    # Iterate over the target languages and generate .mo files
    for language in target_languages:
        settings.LANGUAGE_CODE = language
        call_command('compilemessages')
        # compile_messages(stdout=True)
        

def create_files(json_file_path,project_name):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{project_name}.settings')
    django.setup()
    target_lang=[]
     # Read JSON file
    with open(json_file_path, 'r', encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        os.chdir('locale')
        target_lang=json_data.keys()

    for key,translations in json_data.items():

        os.mkdir(key)
        os.chdir(key)
        os.mkdir('LC_MESSAGES')
        os.chdir('LC_MESSAGES')
        print("Translations: ",key,translations)
        with open('django.po','a') as t:
            t.write('#\n')
            t.write(f"""msgid ""\nmsgstr ""\n""")
            for key,trans in translations.items():
                t.write(f"""msgid "{key}"\nmsgstr "{trans}"\n""")            
        os.chdir('..')
        os.chdir('..')

    file_path=os.getcwd()
    print(file_path)
    custom_compile_messages(target_lang,project_name)


# locale folder 
folder_name = 'locale'  

# check if locale file is already present 1
def create_translator_files(json_file,project_name):
    if not (os.path.exists("locale") and os.path.isdir("locale")):
        os.mkdir('locale')
        create_files(json_file,project_name)
        


def currency_format(currency,language='en-in'):
    
    locale.setlocale(locale.LC_ALL, language)
    return locale.currency(currency, grouping=True)

def number_format(number,lang='en-in'):
    
    locale.setlocale(locale.LC_ALL,lang)
    formatted_value = locale.format_string('%.2f', float(number), grouping=True)
    return formatted_value