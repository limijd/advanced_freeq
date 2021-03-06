#!/usr/bin/env python3

"""advanced_freeq

Usage:
    ./advanced_freeq -t <txtname>  [-o <output>] [-s <mastered>]
    ./advanced_freeq -p <pdfname>  [-o <output>] [-s <mastered>]
    ./advanced_freeq -m <mobiname> [-o <output>] [-s <mastered>]
    ./advanced_freeq -e <epubname> [-o <output>] [-s <mastered>]

Examples:
    ./advanced_freeq -i txtname.txt -o bookfreeq.csv
    ./advanced_freeq -p txtname.pdf -o bookfreeq.csv
    ./advanced_freeq -p txtname.pdf -o bookfreeq.csv -s mastered.csv

Options:
    -h --help           Show this screen.
    -v --version        Show version
    -t --txt            Input Text file
    -p --pdf            Input PDF file
    -m --mobi           Input mobi file
    -e --epub           Input Epub file
    -o --output         Output frequency file
    -s --mastered       Mastered vocabularies file
"""

import os
import sys

SCRIPT_PATH=os.path.dirname(os.path.realpath(__file__))
sys.path.append(SCRIPT_PATH)

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='advanced freeq 0.2')

import numpy as np
import pandas as pd

if arguments['--txt'] == True:
    os.system(
        '%s/freeq.py -i %s -o %s/.book_freeq.csv' % (SCRIPT_PATH, arguments['<txtname>'], SCRIPT_PATH)
    )
elif arguments['--pdf'] == True:
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage
    from io import StringIO

    def convert_pdf_to_txt(path):
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        fp = open(path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos=set()
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
            interpreter.process_page(page)
        fp.close()
        device.close()
        str = retstr.getvalue()
        retstr.close()
        with open('%s/.book.txt'%SCRIPT_PATH, 'w') as book:
            book.write('%s' % str)
    convert_pdf_to_txt(arguments['<pdfname>'])
    os.system('%s/freeq.py -i %s/.book.txt -o %s/.book_freeq.csv'%(SCRIPT_PATH, SCRIPT_PATH, SCRIPT_PATH))

elif arguments['--mobi'] == True:
    os.system('ebook-convert %s %s/.book.txt' %(arguments['<mobiname>'], SCRIPT_PATH))
    os.system('%s/freeq.py -i %s/.book.txt -o %s/.book_freeq.csv'%(SCRIPT_PATH, SCRIPT_PATH, SCRIPT_PATH))
else:
    os.system('ebook-convert %s %s/.book.txt' %(arguments['<epubname>'], SCRIPT_PATH))
    os.system('%s/freeq.py -i %s/.book.txt -o %s/.book_freeq.csv'%(SCRIPT_PATH, SCRIPT_PATH, SCRIPT_PATH))

os.system("sed -i 's/^ *//g' %s/.book_freeq.csv"%SCRIPT_PATH)
os.system("sed -i 's/ /,/g' %s/.book_freeq.csv"%SCRIPT_PATH)

df_book = pd.read_csv('%s/.book_freeq.csv'%SCRIPT_PATH, names=['Freq', 'Word'])
f = lambda x: len(str(x)) > 2
df_book = df_book[df_book['Word'].apply(f)]

if arguments['--mastered'] == False:
    df_coca = pd.read_csv(
        '%s/empty.csv'%SCRIPT_PATH
        #'COCA_top5000.csv'
    ).loc[:,['Rank','Word']]
    df_freq = df_book[~df_book['Word'].isin(df_coca['Word'].iloc[:1000])]
    df_freq.to_csv('%s' % arguments['<output>'], index = None)
    print('All your freeq words are in %s' % arguments['<output>'])

else:
    df_mastered = pd.read_csv(
        '%s' % arguments['<mastered>'], names = ['Index', 'Word']
    )
    df_freq = df_book[~df_book['Word'].isin(df_mastered['Word'])]
    df_freq.to_csv('%s' % arguments['<output>'], index = None)
    print('All your word frequency are in %s' % arguments['<output>'])
