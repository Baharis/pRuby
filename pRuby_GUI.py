import os
from pruby.gui import Application
import tkinter as tk


# MAIN PROGRAM
if __name__ == '__main__':
    root = tk.Tk()
    app_wd = os.path.dirname(os.path.realpath(__file__))
    img_wd = os.path.join(app_wd, 'resources', 'icon.gif')
    Application(root).pack(side='top', fill='both', expand=True)
    root.title('pRuby')
    root.attributes("-topmost", True)
    icon = tk.PhotoImage(file=app_wd + '/resources/icon.gif')
    root.tk.call('wm', 'iconphoto', root._w, icon)
    root.resizable(False, False)
    root.mainloop()
