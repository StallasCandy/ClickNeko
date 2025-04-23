# ClickNeko v1 - Enhanced Safe Macro Tool
# GitHub Repo: https://github.com/StallasCandy/ClickNeko

import threading, time, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Listener as KeyboardListener, KeyCode
from PIL import Image, ImageTk
import random, os, sys, json, webbrowser

mouse = MouseController()
clicking = False
click_thread = None
hotkey = None
hold_mode = False

selected_button = "Left"
click_interval = 0.1
hotkey_char = "z"
click_limit = 0
click_count = 0
click_coords = None
randomize_clicks = False
click_pattern = []
sound_path = None
click_sound_enabled = False

button_map = {
    "Left": Button.left,
    "Right": Button.right,
    "Middle": Button.middle
}

def perform_click_action(action):
    if action == "click":
        mouse.click(button_map[selected_button])
    elif action == "double":
        mouse.click(button_map[selected_button], 2)
    elif action == "hold":
        mouse.press(button_map[selected_button])
    elif action == "release":
        mouse.release(button_map[selected_button])
    elif action.startswith("pause"):
        delay = float(action.split(":")[1])
        time.sleep(delay)

def click_loop():
    global clicking, click_count
    while clicking:
        if click_limit and click_count >= click_limit:
            break
        if click_coords:
            mouse.position = click_coords
        actions = click_pattern or ["click"]
        for act in actions:
            perform_click_action(act)
            if click_sound_enabled and sound_path:
                try:
                    import winsound
                    winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                except:
                    pass
            if randomize_clicks:
                time.sleep(click_interval + random.uniform(-0.02, 0.05))
            else:
                time.sleep(click_interval)
        click_count += 1
    clicking = False

def on_press(key):
    global clicking, click_thread, click_count
    try:
        if key == hotkey:
            if hold_mode:
                clicking = True
                click_count = 0
                click_thread = threading.Thread(target=click_loop)
                click_thread.start()
            else:
                clicking = not clicking
                if clicking:
                    click_count = 0
                    click_thread = threading.Thread(target=click_loop)
                    click_thread.start()
    except:
        pass

def on_release(key):
    global clicking
    if hold_mode and key == hotkey:
        clicking = False

keyboard_listener = KeyboardListener(on_press=on_press, on_release=on_release)
keyboard_listener.start()

def start_gui():
    def apply_settings():
        global selected_button, click_interval, hotkey, hotkey_char, click_limit
        global click_coords, click_sound_enabled, sound_path, hold_mode, randomize_clicks
        try:
            interval = float(interval_entry.get())
            hotkey_input = hotkey_entry.get().strip().lower()
            button_choice = button_choice_var.get()
            limit_input = click_limit_entry.get().strip()
            x, y = coord_x.get().strip(), coord_y.get().strip()
            selected_button = button_choice
            click_interval = interval
            hotkey_char = hotkey_input
            hotkey = KeyCode(char=hotkey_char)
            click_limit = int(limit_input) if limit_input else 0
            click_coords = (int(x), int(y)) if x and y else None
            click_sound_enabled = click_sound_var.get()
            randomize_clicks = randomize_var.get()
            hold_mode = hold_click_var.get()
            status_var.set("Settings applied. Press hotkey to test.")
        except Exception as e:
            status_var.set(f"Error: {e}")

    def choose_sound():
        global sound_path
        sound_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if sound_path:
            sound_label.config(text=os.path.basename(sound_path))

    def show_code():
        webbrowser.open("https://github.com/StallasCandy/ClickNeko")

    def show_info():
        messagebox.showinfo("ClickNeko Info", "ClickNeko is a clean, safe macro clicker for gamers and learners.\nLearn how it works and explore the source code.")

    root = tk.Tk()
    root.title("ClickNeko Macro")
    root.geometry("460x600")
    root.configure(bg="#ffe6f0")

    style = ttk.Style()
    style.theme_use("default")
    style.configure("TLabel", background="#ffe6f0", font=("Comic Sans MS", 10))
    style.configure("TButton", font=("Comic Sans MS", 10), padding=6)
    style.configure("TCheckbutton", background="#ffe6f0")

    try:
        logo_img = Image.open("clickneko_logo.png")
        logo_img = logo_img.resize((120, 120))
        logo = ImageTk.PhotoImage(logo_img)
        tk.Label(root, image=logo, bg="#ffe6f0").pack(pady=(10, 5))
    except:
        pass

    ttk.Label(root, text="Made by Stallas", font=("Comic Sans MS", 14, "bold")).pack(pady=(0, 5))
    ttk.Label(root, text="Safe. Simple. Open-source.", foreground="gray", font=("Comic Sans MS", 9)).pack(pady=(0, 10))

    frame = ttk.Frame(root)
    frame.pack(pady=5)

    ttk.Label(frame, text="Mouse Button:").grid(row=0, column=0, sticky="e")
    button_choice_var = tk.StringVar(value=selected_button)
    ttk.Combobox(frame, textvariable=button_choice_var, values=list(button_map.keys()), state="readonly").grid(row=0, column=1)

    ttk.Label(frame, text="Click Interval (sec):").grid(row=1, column=0, sticky="e")
    interval_entry = ttk.Entry(frame)
    interval_entry.insert(0, str(click_interval))
    interval_entry.grid(row=1, column=1)

    ttk.Label(frame, text="Hotkey:").grid(row=2, column=0, sticky="e")
    hotkey_entry = ttk.Entry(frame)
    hotkey_entry.insert(0, hotkey_char)
    hotkey_entry.grid(row=2, column=1)

    ttk.Label(frame, text="Click Limit (0 = ∞):").grid(row=3, column=0, sticky="e")
    click_limit_entry = ttk.Entry(frame)
    click_limit_entry.insert(0, "0")
    click_limit_entry.grid(row=3, column=1)

    ttk.Label(frame, text="Click X:").grid(row=4, column=0, sticky="e")
    coord_x = ttk.Entry(frame)
    coord_x.grid(row=4, column=1)

    ttk.Label(frame, text="Click Y:").grid(row=5, column=0, sticky="e")
    coord_y = ttk.Entry(frame)
    coord_y.grid(row=5, column=1)

    click_sound_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Enable Sound", variable=click_sound_var).grid(row=6, columnspan=2, pady=5)

    hold_click_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Hold-to-Click Mode", variable=hold_click_var).grid(row=7, columnspan=2)

    randomize_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Humanize Click Delay", variable=randomize_var).grid(row=8, columnspan=2)

    ttk.Button(root, text="Choose Sound", command=choose_sound).pack(pady=5)
    sound_label = ttk.Label(root, text="No sound selected")
    sound_label.pack()

    ttk.Button(root, text="Apply Settings", command=apply_settings).pack(pady=10)
    ttk.Button(root, text="How It Works / Info", command=show_info).pack(pady=2)
    ttk.Button(root, text="View Code on GitHub", command=show_code).pack(pady=2)

    global status_var
    status_var = tk.StringVar(value="Waiting for input...")
    ttk.Label(root, textvariable=status_var, font=("Comic Sans MS", 10, "bold")).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    start_gui()