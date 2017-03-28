#!/usr/bin/env python
"""
Convert google Form to SDAPS tex questionnaire

For further information (manual, description, etc.) please visit:
https://github.com/berteh/gforms2sdaps/

v0.1 (2017-03-23): initial release

The MIT License
Copyright (c) 2017 Berteh (https://github.com/berteh/)
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the 'Software'), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import argparse, sys, os, json, datetime
from pprint import pprint
from string import Template

class CONST:
    """ Constants for general usage
    """
    EMPTY = ''
    AUTHOR = "SDAPS - easy paper enquiries" 
    LANG = "english"

class TEMPLATES:
    """LaTeX templates with placeholders
       some \ characters need to be double to be escaped if they otherwise correspond to a Python character code.
    """
    DOCUMENT = """
\documentclass[
  % Babel language, also used to load translations
  $language,
  % paper size, typically a4paper or letterpaper
  %a4paper, 
  %letterpaper,
  % custom barcode at the center
  %globalid=SDAPS,  %
  % per sheet barcode at the bottom left
  %print_questionnaire_id,
  % twoside is the default, and requires document to be printed and scanned in duplex
  %oneside,
  % Good options to get a better feel for the final look.
  pagemark,
  stamp]{sdaps}
\usepackage[utf8]{inputenc}
% enable to get 2 columns content
%\usepackage{multicol}

\\author{$author}
\\title{$title}

\\begin{document}
  % If you don't like the default text at the beginning of each questionnaire
  % you can remove it with the optional [noinfo] parameter for the environment 
  \\begin{questionnaire}
    % predefined "info" style to hilight some text.
    \\begin{info}
      $description
    \end{info}

    % Use \\addinfo to add metadata (which is printed on the report later on)
    \\addinfo{Date}{$date}
	
	% enable to get 2 columns content
	%\\begin{multicols}{2}

    $questions

    %\end{multicols}

  \end{questionnaire}
\end{document}
"""
        
    TODO="\n\nTODO $title section is not supported yet.\n"

    SHORTTEXT = "\n\n\\textbox{1.5cm}{$title}\n$description\n"
    LONGTEXT = "\n\n\\textbox{3cm}{$title}\n$description\n"
    MULTICHOICE = TODO
    DROPLIST = TODO
    CHECKBOXES = TODO
    SCALE = TODO
    SECTION = "\n\section{$title}\n$description\n"
    MATRIX = TODO
    NEWPAGE = "\n\\newpage\n\section{$title}\n$description\n"
    PHOTO = TODO
    VIDEO = TODO
    

#defaults
outDir = os.getcwd()
question_types = {
    0:TEMPLATES.SHORTTEXT, 
    1:TEMPLATES.LONGTEXT, 
    2:TEMPLATES.MULTICHOICE, 
    3:TEMPLATES.DROPLIST, 
    4:TEMPLATES.CHECKBOXES,
    5:TEMPLATES.SCALE, 
    6:TEMPLATES.SECTION,
    7:TEMPLATES.MATRIX,
    8:TEMPLATES.NEWPAGE,
    11:TEMPLATES.PHOTO,
    12:TEMPLATES.VIDEO}

#parse options
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''Convert google Form to SDAPS tex questionnaire''',  
    usage="%(prog)s [options] infiles+",
    epilog='''requirements
    This program requires Python 2.7+

examples:

 more information: https://github.com/berteh/gforms2sdaps/
 ''')
parser.add_argument('infiles', default=['test/FB_PUBLIC_LOAD_DATA_.json'], nargs='?',
    help='input HTML file(s) of google forms to convert to SDAPS, wildcards are supported')
parser.add_argument('-o', '--outName', default=None, 
    help='name of single output file, or output directory for multiple inputs (that will be created if it does not readily exists).')
parser.add_argument('-a', '--author', default=CONST.AUTHOR,
    help='author of the questionnaire, defaults to "SDAPS"')
parser.add_argument('-d', '--date', default=datetime.date.today(),
    help='author of the questionnaire, defaults to "SDAPS"')
parser.add_argument('-l', '--language', default=CONST.LANG,
    help='language of the questionnaire, in LaTeX format, default is english')
#parser.add_argument('-i', '--image', default=CONST.SDPASLOGO
#    help='image to display in the header')


def ife(test, if_result, else_result):
    """ Utility if-then-else syntactic sugar
    """
    if(test):
        return if_result
    return else_result

#handle arguments
args = parser.parse_args()

# create output directory if needed
if ((len(args.infiles)>1) and (not(args.outName is None)) and (not os.path.exists(args.outName))):
    os.makedirs(args.outName)


def apply_template(template, subs):
    s = Template(template)
    return(s.safe_substitute(subs))

def convert_question(data):
    subs = {'title': ife((data[1] is None), '', data[1]), 
            'description': ife((data[2] is None), '', data[2]) }
    if(len(data)>4):
        subs['options'] = data[4]
    return(apply_template(question_types[data[3]], subs))

#run
for infile in args.infiles:
    with open(infile) as data_file:    
        #print("reading file %s"%data_file)
        data_all = json.load(data_file)
        data = data_all[1]

        questions_texts = []
        for data_question in data[1]:
            questions_texts.append(convert_question(data_question))


        #fet: u' '.join(questions_texts)
        questions = ''.join(questions_texts)

        subs = {'author':args.author, 'date':args.date, 'language':args.language, 'banner_img':None,
                'title':data[8], 'description':data[0], 'questions':questions}
        document = apply_template(TEMPLATES.DOCUMENT, subs)

        print(document.encode('utf-8'))
