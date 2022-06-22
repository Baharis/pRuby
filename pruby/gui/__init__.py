import tkinter as tk
from pruby.gui.app import Application
from pruby.resources import icon


def run():
    root = tk.Tk()
    Application(root).pack(side='top', fill='both', expand=True)
    root.title('pRuby')
    root.attributes("-topmost", True)
    root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(data=icon))
    root.resizable(False, False)
    root.mainloop()
