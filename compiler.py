import customtkinter as ctk
import serial
import serial.tools.list_ports
from tkinter import filedialog, messagebox

# ---------------- Serial Communication ---------------- #
ser = None

def list_ports():
    """ List available serial ports """
    return [port.device for port in serial.tools.list_ports.comports()]

def refresh_ports():
    """Refresh the available serial ports and update the dropdown menu."""
    ports = list_ports()  # Get available ports
    if ports:
        port_menu.configure(values=ports)
        port_var.set(ports[0])  # Set to first available port
    else:
        port_menu.configure(values=["No Ports Found"])
        port_var.set("No Ports Found")
    log_message("Ports refreshed.")

def connect_serial():
    """ Connect to the selected serial port """
    global ser
    selected_port = port_var.get()
    baud_rate = int(baud_var.get())

    try:
        ser = serial.Serial(selected_port, baud_rate, timeout=1)
        log_message(f"Connected to {selected_port}")
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

def list_task():
    """Send <LIST> command to ATMega328P and display received task list in monitor"""
    global ser
    if not ser or not ser.is_open:
        messagebox.showwarning("Error", "Not connected to serial port!")
        return

    try:
        ser.write(b"<LIST>\n")  # Send the <LIST> command
        log_message("> <LIST>", "terminal")  # Log in terminal
        
        response = []
        ser.timeout = 2
        while ser.in_waiting or len(response) == 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                response.append(line)

        if response:
            log_message("\n".join(response), "monitor")  # Only list tasks in monitor
        else:
            log_message("No tasks found.", "monitor")

    except Exception as e:
        log_message(f"Error: {str(e)}", "terminal")  # Errors go to terminal

        
def debug_task():
    """Send <DEBUG> command to ATMega328P and display received debug info in monitor"""
    global ser
    if not ser or not ser.is_open:
        messagebox.showwarning("Error", "Not connected to serial port!")
        return

    try:
        ser.write(b"<DEBUG>\n")  # Send the <DEBUG> command
        log_message("> <DEBUG>", "terminal")  # Log the sent command in terminal
        
        # Wait and read response from ATMega328P
        response = []
        ser.timeout = 2  # Set a timeout for reading
        while ser.in_waiting or len(response) == 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                response.append(line)

        # Display the received debug information in monitor
        if response:
            log_message("\n".join(response), "monitor")  # Debug info only in monitor
        else:
            log_message("No debug information received.", "monitor")

    except Exception as e:
        log_message(f"Error: {str(e)}", "terminal")  # Errors go to terminal



def send_command():
    """ Send command from input field """
    global ser
    if ser and ser.is_open:
        command = command_entry.get().strip()
        if command:
            ser.write((command + "\n").encode())
            log_message(f"> {command}")
            command_entry.delete(0, ctk.END)

def read_serial():
    """ Read incoming data """
    global ser
    if ser and ser.is_open:
        try:
            while ser.in_waiting:
                data = ser.readline().decode('utf-8', errors='ignore').strip()
                if data:
                    log_message(data)
        except Exception as e:
            log_message(f"Error: {str(e)}")
    root.after(100, read_serial)

def send_task_file():
    """ Send a binary task file """
    global ser
    if not ser or not ser.is_open:
        messagebox.showwarning("Error", "Not connected to serial port!")
        return
    
    file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])
    if not file_path:
        return

    try:
        with open(file_path, "rb") as file:
            data = file.read()
            ser.write(b"<TASK:")
            ser.write(data)
            ser.write(b">")
            log_message(f"Sent task file: {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send file\n{str(e)}")

def log_message(msg, target="terminal"):
    """Log messages to the selected monitor (Read-Only)"""
    
    # Choose target monitor: 'terminal' for serial communication, 'monitor' for List & Debug only
    if target == "terminal":
        terminal_monitor.configure(state="normal")
        terminal_monitor.insert(ctk.END, msg + "\n")
        terminal_monitor.yview(ctk.END)
        terminal_monitor.configure(state="disabled")  # Re-enable read-only
    elif target == "monitor":
        monitor.configure(state="normal") 
        monitor.insert(ctk.END, msg + "\n")
        monitor.yview(ctk.END)
        monitor.configure(state="disabled")  # Re-enable read-only


# ---------------- GUI Setup ---------------- #
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("ATMega328P Serial Monitor & Task Sender")

# Let Tkinter calculate the required size
root.update_idletasks()
root.minsize(root.winfo_width(), root.winfo_height())  # Set minimum size based on content

#root.resizable(False, False)  # Disable resizing (optional)


# Port Selection
port_var = ctk.StringVar(value=list_ports()[0] if list_ports() else "No Ports Found")
port_label = ctk.CTkLabel(root, text="Port:")
port_label.grid(row=0, column=0, padx=5, pady=5)

port_menu = ctk.CTkOptionMenu(root, variable=port_var, values=list_ports())
port_menu.grid(row=0, column=1, padx=5, pady=5)

# Refresh Button (Move it properly behind the Port dropdown)
refresh_btn = ctk.CTkButton(root, text="⟳", width=40, command=refresh_ports)
refresh_btn.grid(row=0, column=2, padx=5, pady=5)

# Baud Rate Selection (Move to column 3)
baud_var = ctk.StringVar(value="9600")
baud_label = ctk.CTkLabel(root, text="Baud:")
baud_label.grid(row=0, column=3, padx=5, pady=5)

baud_menu = ctk.CTkOptionMenu(root, variable=baud_var, values=["9600", "115200", "57600", "4800", "1200"])
baud_menu.grid(row=0, column=4, padx=5, pady=5)

# Connect & Disconnect Buttons (Shift to next columns)
connect_btn = ctk.CTkButton(root, text="Connect", command=connect_serial)
connect_btn.grid(row=0, column=5, padx=5, pady=5)

disconnect_btn = ctk.CTkButton(root, text="Disconnect", command=disconnect_serial)
disconnect_btn.grid(row=0, column=6, padx=5, pady=5)


# Serial Monitor (Auto Resize)
monitor = ctk.CTkTextbox(root, height=250, wrap="word")  # Removed fixed width
monitor.grid(row=1, column=0, columnspan=7, padx=5, pady=5, sticky="nsew")  # Auto expand
monitor.configure(state="disabled")

# Terminal Monitor (For all Serial Communication)
terminal_monitor = ctk.CTkTextbox(root, width=420, height=150, wrap="word")
terminal_monitor.grid(row=2, column=0, columnspan=7, padx=5, pady=5, sticky="w")

#<LIST> Button
list_btn = ctk.CTkButton(root, text="List Task", command=list_task)
list_btn.grid(row=2, column=5,columnspan=7, padx=5, pady=5, sticky="wn")

#<DEBUG> Button
debug_btn = ctk.CTkButton(root, text="Debug", command=debug_task)
debug_btn.grid(row=2, column=6, columnspan=7,padx=5, pady=5, sticky="wn")

# Read-Only Terminal Monitor
#terminal_monitor.configure(state="disabled")



#Command Entry
#command_entry = ctk.CTkEntry(root, width=400)
#command_entry.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
#send_btn = ctk.CTkButton(root, text="Send", command=send_command)
#send_btn.grid(row=2, column=4, columnspan=2, padx=5, pady=5)




# Send Task File Button
#task_btn = ctk.CTkButton(root, text="Send Task File", command=send_task_file)
#task_btn.grid(row=3, column=0, columnspan=6, padx=5, pady=10)

# Auto Read Serial Data
root.after(100, read_serial)
root.mainloop()
