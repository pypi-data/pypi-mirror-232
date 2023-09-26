# i18n engine for django-framework
###  internationalization and localization in django

This Python package provides functionality to generate translation files for Django projects based on JSON file data.

## Author

* [Viraj B. Poojari](virajp.in@mouritech.com)

## Installation

* To install the package, use the following command:

```cmd
pip install mt_django_i18n
```
## Setup
Before using library, you need setup some things in your django project, please follow this steps

1. Setup all required variables in your settings.py
```py
from django.utils.translation import gettext_lazy as _
# Mention the lanuage with respective language code which you will be using in your project
LANGUAGES = [
    ('en', _('English')),
    ('fr', _('French')),
   ('es', _('Spanish')),
   ('de',_('German')),
   ('en-IN',_('English (India)'))
    # Add more languages as needed

]

LANGUAGE_CODE = 'en-in' # default =  'en'

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),  # Optional, default path './locales' folder
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N=True

LANGUAGES_BIDI = [
    'he', 'ar',  # Add right-to-left languages if required
]

# Below mention localization of number system according to current language code of project

THOUSAND_SEPARATOR=','
DECIMAL_SEPARATOR='.'
USE_THOUSAND_SEPARATOR=True
NUMBER_GROUPING=(3,2,0)

```
2. Create a JSON file with translation data in the following format:

```json
{
  "fr": {
    "Hello": "Bonjour",
    "Goodbye": "Au revoir"
  },
  "de": {
    "Hello": "Hallo",
    "Goodbye": "Auf Wiedersehen"
  },
  "es": {
    "Hello": "Hola",
    "Goodbye": "Adiós"
  }
}
```

3. Import and use the create_files() function from the translation_file_generator module:
```py
    from mt_django_i18n.json_to_po import create_translator_files
    from django.utils.translation import gettext as _

    create_files(json_file_path,project_name,target_lang)

```
1. _**json_file_path** = This parameter represent file path for translation_
2. _**project_name** = Name of project_ 
3. _**target_lang** = Lagunages which language file should be converted in binary format file i.e .mo files_

## Example
### views.py
```py
from mt_i18n.json_to_po import create_files
import os
from django.utils.translation import gettext as _
# Create your views here.


def blog(request):
    'hello':_('Hello'), # this mark to value stored in _('') are to translated 
    if not (os.path.exists("locale") and os.path.isdir("locale")):
        
        os.mkdir('locale')
        create_files("translator.json","blog",['fr', 'de', 'es'] )
    
```

## Templates - HTML pages
* The static text to be translated should be marked throught {% trans Hello world! %} or via variable format
as mention below 
```html
    <p>{{example}}</p>
    <p>{% trans %}</p>
```
* For localization
```html
                    {% load l10n %}
                    {% localize on %}
                    <tr>
                      <td><h6 class="text-muted">Category</h6></td>
                      <td> <h6 class="fw-bold">
                        {{my_currency|localize}}
                      </h6></td>
                    </tr>

                    <tr>
                      <td><h6 class="text-muted">Number</h6></td>
                      <td> <h6 class="fw-bold">{{my_number|localize}}
                      </h6></td>
                    </tr>

                    <tr>
                      <td><h6 class="text-muted">Date</h6></td>
                      <td> <h6 class="fw-bold">
                        {{my_date}}
                      </h6></td>
                    </tr>
                  </tbody>
                </table>
                {% endlocalize %}
```
## #currency_format
* This function help to convert the number into currency format by passing number and language code as shown in below syntax

```py
 from mt_django_i18n.json_to_po import currency_format
 my_currency= currency_format(currency,language='en-in') 
```
* Where _currency_ parameter is for passing number/currency and _language_ parameter for language code.

### Example
```py
 from mt_django_i18n.json_to_po import currency_format
 my_currency = currency_format(currency=1234567.89,language=request.LANGUAGE_CODE) 
```
**Note**
Use _translation_ package to current activate language of project.

```py
from django.utils import translation
translation.activate(language)
```

## #number_format
* This function help to convert the number into number format by passing number and language code as shown in below syntax

```py
 from mt_django_i18n.json_to_po import number_format
 my_number= number_format(number,lang='en-in')
```
* Where _number_ parameter is for pass number and _lang_ parameter is for language code.

## Example
```py
 from mt_django_i18n.json_to_po import number_format 
 from decimal import *
  my_number=number_format(Decimal(1000000.50) ,lang=request.LANGUAGE_CODE)
```
## urls.py
```py
from django.conf.urls.i18n import i18n_patterns
urlpatterns+=i18n_patterns(
  
    path('',blog,name="blog"),
    # path('language_select/',language_select,name="language_select")
)
```

```note
# Note: activate the language code of project every time there is
change in language so that translation perform better. 

from django.utils import translation.
translation.activate(language)
``` 
