import sys
import tkinter
from tkinter import ScrolledText

class APP(object):

    def __init__(self, root):
        super(APP, self).__init__()
        self.root = root
        self.root.title("System Controller")
        self.frame = tkinter.Frame(root)
        self.frame.pack()
        self.text = ScrolledText.ScrolledText(self.Frame)
        redir = RedirectText(self.text)
        sys.stdout = redir
