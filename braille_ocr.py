import serial
import time
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import pytesseract
import cv2

# ---- SETTINGS ----
COM_PORT = 'COM3'
BAUD_RATE = 9600
DELAY = 0.4
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

ser = None
cap = None

def connect():
    global ser
    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        status_label.config(text="Arduino Connected ✅", fg="green")
        log("Connected to Arduino on COM3")
    except:
        messagebox.showerror("Error", "Could not connect to Arduino!\nCheck CP2102 is plugged in!")

def disconnect():
    global ser
    try:
        ser.close()
        status_label.config(text="Disconnected", fg="red")
        log("Disconnected from Arduino")
    except:
        pass

def send_to_arduino(text):
    if not ser or not ser.is_open:
        messagebox.showerror("Error", "Connect to Arduino first!")
        return
    text = text.upper()
    log(f"Sending: {text}")
    for char in text:
        if char == ' ':
            time.sleep(DELAY)
            continue
        if char.isalpha():
            ser.write(char.encode())
            status_label.config(text=f"Sending: {char}", fg="orange")
            log(f"Sent character: {char}")
            root.update()
            time.sleep(DELAY)
    status_label.config(text="Done! All characters sent ✅", fg="green")
    log("All characters sent!")

def ocr_and_send(image):
    # Run OCR
    text = pytesseract.image_to_string(image)
    text = ''.join(filter(lambda c: c.isalpha() or c == ' ', text))
    text = text.strip()
    log(f"OCR Result: {text}")
    ocr_text.delete(1.0, tk.END)
    ocr_text.insert(tk.END, text)
    if text:
        send_to_arduino(text)
    else:
        messagebox.showwarning("No Text", "No text found in image!")

def upload_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
    )
    if file_path:
        image = Image.open(file_path)
        show_preview(image)
        log("Image uploaded")
        ocr_and_send(image)

def capture_image():
    global cap
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "No camera found!")
        return
    ret, frame = cap.read()
    if ret:
        cap.release()
        # Convert for OCR
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb)
        show_preview(image)
        log("Image captured from camera")
        ocr_and_send(image)
    else:
        messagebox.showerror("Error", "Could not capture image!")

def show_preview(image):
    image.thumbnail((300, 200))
    photo = ImageTk.PhotoImage(image)
    preview_label.config(image=photo)
    preview_label.image = photo

def send_manual():
    text = manual_entry.get()
    if text:
        send_to_arduino(text)
    else:
        messagebox.showwarning("Empty", "Enter some text first!")

def log(msg):
    log_box.insert(tk.END, f"> {msg}\n")
    log_box.see(tk.END)

# ---- GUI ----
root = tk.Tk()
root.title("Braille OCR Sender")
root.geometry("500x650")
root.configure(bg="#f0f0f0")

tk.Label(root, text="BRAILLE OCR SENDER", font=("Arial", 16, "bold"),
         bg="#f0f0f0").pack(pady=10)

# Connection
conn_frame = tk.Frame(root, bg="#f0f0f0")
conn_frame.pack()
tk.Button(conn_frame, text="Connect Arduino", command=connect,
          bg="#4CAF50", fg="white", font=("Arial", 10), width=15).grid(row=0, column=0, padx=5)
tk.Button(conn_frame, text="Disconnect", command=disconnect,
          bg="#f44336", fg="white", font=("Arial", 10), width=15).grid(row=0, column=1, padx=5)

status_label = tk.Label(root, text="Not Connected", font=("Arial", 11),
                         bg="#f0f0f0", fg="red")
status_label.pack(pady=5)

# Image buttons
tk.Label(root, text="── Get Image ──", font=("Arial", 11),
         bg="#f0f0f0").pack(pady=5)
img_frame = tk.Frame(root, bg="#f0f0f0")
img_frame.pack()
tk.Button(img_frame, text="📷 Capture from Camera", command=capture_image,
          bg="#2196F3", fg="white", font=("Arial", 11), width=20).grid(row=0, column=0, padx=5, pady=3)
tk.Button(img_frame, text="🖼 Upload Image", command=upload_image,
          bg="#9C27B0", fg="white", font=("Arial", 11), width=20).grid(row=1, column=0, padx=5, pady=3)

# Preview
preview_label = tk.Label(root, bg="#cccccc", width=40, height=8)
preview_label.pack(pady=5)

# OCR Result
tk.Label(root, text="OCR Text Found:", font=("Arial", 10, "bold"),
         bg="#f0f0f0").pack()
ocr_text = tk.Text(root, height=3, width=45, font=("Arial", 10))
ocr_text.pack(pady=3)

# Manual entry
tk.Label(root, text="── Or Type Manually ──", font=("Arial", 11),
         bg="#f0f0f0").pack(pady=3)
manual_entry = tk.Entry(root, font=("Arial", 13), width=25)
manual_entry.pack()
tk.Button(root, text="Send Manual Text", command=send_manual,
          bg="#FF9800", fg="white", font=("Arial", 11), width=20).pack(pady=5)

# Log
tk.Label(root, text="Log:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack()
log_box = tk.Text(root, height=5, width=55, font=("Arial", 9), bg="#1e1e1e", fg="#00ff00")
log_box.pack(pady=5)

root.mainloop()

