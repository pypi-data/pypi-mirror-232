import time
import tkinter as tk
from tkinter import simpledialog

root = tk.Tk()
root.withdraw()  # Hide the main window


prompt = "Hey! It looks like you've been away away. What have you been doing?"
title = "AFK Checkin"


def on_key(event):
    # Check for Ctrl + Backspace
    if event.keysym == "BackSpace" and event.state == 4:
        text_widget = event.widget
        # Delete the word
        text_widget.delete("insert-1c wordstart", "insert")


simpledialog.askstring.bind("<Key>", on_key)
response = simpledialog.askstring(prompt, title)
