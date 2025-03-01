import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox

# ---------------- Serial Communication ---------------- #
ser = None

def list_ports():
    """ List available serial ports """
    return [port.device for port in serial.tools.list_ports.comports()]

def connect_serial():
    """ Connect to the selected serial port """
    global ser
    selected_port = port_var.get()
    baud_rate = int(baud_var.get())

    try:
        ser = serial.Serial(selected_port, baud_rate, timeout=1)
        log_message("Connected to " + selected_port)
    except serial.SerialException as e:
        messagebox.showerror("Connection Error", str(e))
        ser = None

def disconnect_serial():
    """ Disconnect the serial port """
    global ser
    if ser:
        ser.close()
        log_message("Disconnected")
        ser = None

def send_command():
    """ Send command from input field """
    global ser
    if ser and ser.is_open:
        command = command_entry.get().strip()
        if command:
            ser.write((command + "\n").encode())  # Send command
            log_message("> " + command)
            command_entry.delete(0, tk.END)

def read_serial():
    """ Read incoming data from the ATMega328P """
    global ser
    if ser and ser.is_open:
        try:
            while ser.in_waiting:
                data = ser.readline().decode('utf-8', errors='ignore').strip()
                if data:
                    log_message(data)
        except Exception as e:
            log_message("Error: " + str(e))
    root.after(100, read_serial)

# ---------------- Task File Sending ---------------- #
def send_task_file():
    """ Send a binary task file to the ATMega328P """
    global ser
    if not ser or not ser.is_open:
        messagebox.showwarning("Error", "Not connected to serial port!")
        return
    
    file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])
    if not file_path:
        return  # User canceled

    try:
        with open(file_path, "rb") as file:
            data = file.read()
            ser.write(b"<TASK:")  # Start of task command
            ser.write(data)       # Send binary file content
            ser.write(b">")       # End of task command
            log_message("Sent task file: " + file_path)
    except Exception as e:
        messagebox.showerror("Error", "Failed to send file\n" + str(e))

# ---------------- UI Functions ---------------- #
def log_message(msg):
    """ Log messages to the Serial Monitor """
    monitor.insert(tk.END, msg + "\n")
    monitor.yview(tk.END)

# ---------------- GUI Setup ---------------- #
root = tk.Tk()
root.title("ATMega328P Serial Monitor & Task Sender")
root.geometry("600x500")

# Port Selection
tk.Label(root, text="Port:").grid(row=0, column=0, padx=5, pady=5)
port_var = tk.StringVar(value=list_ports()[0] if list_ports() else "")
port_menu = tk.OptionMenu(root, port_var, *list_ports())
port_menu.grid(row=0, column=1, padx=5, pady=5)

# Baud Rate Selection
tk.Label(root, text="Baud:").grid(row=0, column=2, padx=5, pady=5)
baud_var = tk.StringVar(value="9600")
baud_menu = tk.OptionMenu(root, baud_var, "9600", "115200", "57600", "4800", "1200")
baud_menu.grid(row=0, column=3, padx=5, pady=5)

# Connect & Disconnect Buttons
connect_btn = tk.Button(root, text="Connect", command=connect_serial)
connect_btn.grid(row=0, column=4, padx=5, pady=5)

disconnect_btn = tk.Button(root, text="Disconnect", command=disconnect_serial)
disconnect_btn.grid(row=0, column=5, padx=5, pady=5)

# Serial Monitor
monitor = scrolledtext.ScrolledText(root, height=15, width=70)
monitor.grid(row=1, column=0, columnspan=6, padx=5, pady=5)

# Command Entry
command_entry = tk.Entry(root, width=50)
command_entry.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
send_btn = tk.Button(root, text="Send", command=send_command)
send_btn.grid(row=2, column=4, columnspan=2, padx=5, pady=5)

# Send Task File Button
task_btn = tk.Button(root, text="Send Task File", command=send_task_file)
task_btn.grid(row=3, column=0, columnspan=6, padx=5, pady=10)

# Auto Read Serial Data
root.after(100, read_serial)
root.mainloop()
