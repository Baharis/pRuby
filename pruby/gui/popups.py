import os
import tkinter.filedialog as fd
import tkinter.messagebox as mb


def open_file_dialogue():
    title = 'Open ruby spectrum file...'
    filetypes = (("Text files", "*.txt"), ("All files", "*.*"))
    wdir = os.getcwd()
    return fd.askopenfilename(title=title, filetypes=filetypes, initialdir=wdir)


def show_about():
    message = 'pRuby - pressure estimation based on ruby fluorescence ' \
              'spectrum by Daniel Tcho\u0144\n\n' \
              'For details and help, visit pRuby page ' \
              '(https://github.com/Baharis/pRuby)' \
              'or contact dtchon@chem.uw.edu.pl.'
    mb.showinfo(title='About pRuby', message=message)
