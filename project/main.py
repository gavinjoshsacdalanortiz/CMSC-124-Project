import tkinter as tk
from gui import LOLCodeInterpreterGUI

# Entry point for LOL CODE interpreter
def main():
    # initialize main application window, create + run GUI app and start event loop
    root = tk.Tk()
    app = LOLCodeInterpreterGUI(root)
    root.mainloop()
    
main()