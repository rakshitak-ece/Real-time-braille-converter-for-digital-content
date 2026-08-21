import serial
import time
import tkinter as tk
from tkinter import messagebox

COM_PORT = 'COM3'
BAUD_RATE = 9600
DELAY = 0.4

def connect():
    global ser
    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        status_label.config(text="Connected ✅", fg="green")
        send_button.config(state="normal")
    except:
        messagebox.showerror("Error", f"Could not open COM3!\nCheck if CP2102 is plugged in!")

def send_text():
    text = text_entry.get()
    if not text:
        messagebox.showwarning("Empty", "Please enter some text!")
        return
    status_label.config(text="Sending...", fg="orange")
    root.update()
    for char in text:
        if char == ' ':
            time.sleep(DELAY)
            continue
        ser.write(char.encode())
        char_label.config(text=f"Sending: {char.upper()}")
        root.update()
        time.sleep(DELAY)
    status_label.config(text="Done! ✅", fg="green")
    char_label.config(text="All characters sent!")

def disconnect():
    try:
        ser.close()
        status_label.config(text="Disconnected", fg="red")
        send_button.config(state="disabled")
    except:
        pass

root = tk.Tk()
root.title("Braille Sender")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

tk.Label(root, text="BRAILLE SENDER", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=10)
tk.Label(root, text="Enter Text:", font=("Arial", 12), bg="#f0f0f0").pack()
text_entry = tk.Entry(root, font=("Arial", 14), width=25)
text_entry.pack(pady=5)

tk.Button(root, text="Connect to Arduino", command=connect,
          bg="#4CAF50", fg="white", font=("Arial", 11), width=20).pack(pady=5)

send_button = tk.Button(root, text="Send to Braille", command=send_text,
          bg="#2196F3", fg="white", font=("Arial", 11), width=20, state="disabled")
send_button.pack(pady=5)

tk.Button(root, text="Disconnect", command=disconnect,
          bg="#f44336", fg="white", font=("Arial", 11), width=20).pack(pady=5)

status_label = tk.Label(root, text="Not Connected", font=("Arial", 11), bg="#f0f0f0", fg="red")
status_label.pack(pady=5)

char_label = tk.Label(root, text="", font=("Arial", 11), bg="#f0f0f0", fg="blue")
char_label.pack(pady=5)

root.mainloop()
