import json
import tkinter as tk
from build_canvas import SimpleOribitalSimulation

def load_config():
    """
    Load config file
    """
    f = open("config.json", encoding="utf-8")
    return json.load(f)

if __name__ == '__main__':
    root = tk.Tk()
    config = load_config()
    SimpleOribitalSimulation(root, config)
    root.mainloop()
    