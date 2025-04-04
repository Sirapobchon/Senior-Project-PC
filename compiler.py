import customtkinter as ctk
import serial
import serial.tools.list_ports
import time
from tkinter import filedialog, messagebox
import os

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
    log_terminal("Ports refreshed.")

def connect_serial():
    """ Connect to the selected serial port """
    global ser
    selected_port = port_var.get()
    baud_rate = int(baud_var.get())

    try:
        ser = serial.Serial(selected_port, baud_rate, timeout=1)
        log_terminal(f"Connected to {selected_port}")
    except serial.SerialException as e:
        log_terminal(str(e))
        messagebox.showerror("Connection Error", str(e))
        ser = None

def disconnect_serial():
    """ Disconnect the serial port """
    global ser
    if ser:
        ser.close()
        log_terminal("Disconnected")
        ser = None

def list_task():
    global ser
    if not ser or not ser.is_open:
        log_terminal("Not connected to serial port!")
        messagebox.showwarning("Error", "Not connected to serial port!")
        return

    try:
        ser.reset_input_buffer()  # Clear old data
        ser.write(b"<LIST>\n")  # Send <LIST> command
        log_terminal("Sending <LIST> Command...")  

        # time.sleep(0.5)  # Short delay for MCU response

        start_time = time.time()
        timeout_seconds = 2
        response = []
        found_task = False  # Track if any task is found

        while time.time() - start_time < timeout_seconds:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    if "Slot" in line or "T ID" in line:
                        log_message(line)
                        found_task = True
                    elif line != "List of Tasks:" and line != "No stored tasks found.":
                        response.append(line)
            else:
                time.sleep(0.1)  # Prevent CPU overuse
        
        # Show first received line normally in the terminal
        if response:
            log_terminal(f"{response[0]}")  # Show first valid response
        
        # If no tasks found, display message in the terminal
        if not found_task:
            log_terminal("No tasks found.")

    except Exception as e:
        log_terminal(f"Error: {str(e)}")  # Handle errors




        
def debug_task():
    global ser
    if not ser or not ser.is_open:
        log_terminal("Not connected to serial port!")
        messagebox.showwarning("Error", "Not connected to serial port!")
        return

    try:
        log_terminal("Sending <DEBUG> Command...")  # Show sent command in monitor
        ser.write(b"<DEBUG>\n")  # Send the <DEBUG> command

        time.sleep(0.5)  # Short delay for MCU response
        
        # Wait and read response from ATMega328P
        response = []
        start_time = time.time()
        while time.time() - start_time < 2:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                response.append(line)

        # Display everything (sent command + received response) in monitor
        if response:
            log_message("\n".join(response))  # Debug info only in monitor
        else:
            log_message("No debug information received.")

    except Exception as e:
        log_message(f"Error: {str(e)}")  # Now errors also go to monitor

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
    """ Send a precompiled binary task file to the RTOS with a proper header. """
    global ser
    if not ser or not ser.is_open:
        messagebox.showwarning("Error", "Not connected to serial port!")
        return

    file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])
    if not file_path:
        return
        
    # --- Popup: Ask for Task Parameters ---
    popup = ctk.CTkToplevel(root)
    popup.title("Task Configuration")
    popup.geometry("300x300")

    ctk.CTkLabel(popup, text="Task ID (0-9):").pack(pady=(10, 0))
    id_entry = ctk.CTkEntry(popup)
    id_entry.pack()

    ctk.CTkLabel(popup, text="Task Type (0=GPIO, 1=PWM, etc):").pack(pady=(10, 0))
    type_entry = ctk.CTkEntry(popup)
    type_entry.pack()

    ctk.CTkLabel(popup, text="Priority (1=Low .. 3=High):").pack(pady=(10, 0))
    priority_entry = ctk.CTkEntry(popup)
    priority_entry.pack()

    def submit_task_info():
        try:
            task_id = int(id_entry.get())
            task_type = int(type_entry.get())
            task_priority = int(priority_entry.get())

            if not (0 <= task_id <= 9):
                raise ValueError("Task ID must be between 0–9")

            with open(file_path, "rb") as file:
                binary_data = file.read()

            binary_size = len(binary_data)
            if binary_size > 512:
                messagebox.showwarning("Too Large", "Binary exceeds 512-byte task limit.")
                popup.destroy()
                return

            status = 1  # Running
            flash_address = (0).to_bytes(4, 'little')  # Not used yet

            header = bytes([
                task_id,
                task_type,
                task_priority,
                binary_size & 0xFF,
                (binary_size >> 8) & 0xFF,
                status
            ]) + flash_address # 6 + 4 = 10 bytes total

            full_packet = b"<TASK:" + header + binary_data + b">"
            
            ser.reset_input_buffer()
            ser.write(full_packet)
            filename = os.path.basename(file_path)
            log_terminal(f"Sent task '{filename}' with ID={task_id}, Type={task_type}, Size={binary_size}")
            
            time.sleep(0.5)  # Give MCU time to process and respond

            response = []
            start_time = time.time()
            while time.time() - start_time < 2:
                if ser.in_waiting:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        response.append(line)
                else:
                    time.sleep(0.05)

            if response:
                for line in response:
                    log_message(line)
            
            popup.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input or file\n{str(e)}")
            popup.destroy()

    send_btn = ctk.CTkButton(popup, text="Send Task", command=submit_task_info)
    send_btn.pack(pady=20)

def clear_monitor():
    """Clear both the main monitor and the terminal monitor."""
    monitor.configure(state="normal")  # Enable editing
    monitor.delete("1.0", ctk.END)  # Clear content
    monitor.configure(state="disabled")  # Disable editing again

    terminal_monitor.configure(state="normal")  # Enable editing
    terminal_monitor.delete("1.0", ctk.END)  # Clear content
    terminal_monitor.configure(state="disabled")  # Disable editing again


def log_message(msg):
        monitor.configure(state="normal") 
        monitor.insert(ctk.END, msg + "\n")
        monitor.yview(ctk.END)
        monitor.configure(state="disabled")  # Re-enable read-only

def log_terminal(msg):
        terminal_monitor.configure(state="normal")
        terminal_monitor.insert(ctk.END, msg + "\n")
        terminal_monitor.yview(ctk.END)
        terminal_monitor.configure(state="disabled")  # Re-enable read-only

# ---------------- GUI Setup ---------------- #
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("ATMega328P Serial Monitor & Task Sender")

# Port Selection Frame (row 0 only)
port_frame = ctk.CTkFrame(root)
port_frame.grid(row=0, column=0, columnspan=7, padx=5, pady=5, sticky="ew")

port_var = ctk.StringVar(value=list_ports()[0] if list_ports() else "No Ports Found")
port_label = ctk.CTkLabel(port_frame, text="Port:")
port_label.grid(row=0, column=0, padx=5, pady=5)

port_menu = ctk.CTkOptionMenu(port_frame, variable=port_var, values=list_ports())
port_menu.grid(row=0, column=1, padx=5, pady=5)

refresh_btn = ctk.CTkButton(port_frame, text="⟳", width=40, command=refresh_ports)
refresh_btn.grid(row=0, column=2, padx=5, pady=5)

baud_var = ctk.StringVar(value="9600")
baud_label = ctk.CTkLabel(port_frame, text="Baud:")
baud_label.grid(row=0, column=3, padx=5, pady=5)

baud_menu = ctk.CTkOptionMenu(port_frame, variable=baud_var, values=["9600", "115200", "57600", "4800", "1200"])
baud_menu.grid(row=0, column=4, padx=5, pady=5)

connect_btn = ctk.CTkButton(port_frame, text="Connect", command=connect_serial)
connect_btn.grid(row=0, column=5, padx=5, pady=5)

disconnect_btn = ctk.CTkButton(port_frame, text="Disconnect", command=disconnect_serial)
disconnect_btn.grid(row=0, column=6, padx=5, pady=5)

# Serial Monitor (Auto Resize)
monitor = ctk.CTkTextbox(root, height=250, wrap="word", state="disabled")
monitor.grid(row=1, column=0, columnspan=7, padx=5, pady=5, sticky="nsew")

# Row 2 Frames: Terminal and Button Section (Equal Size)
row2_frame = ctk.CTkFrame(root)
row2_frame.grid(row=2, column=0, columnspan=7, padx=5, pady=5, sticky="nsew")
row2_frame.grid_columnconfigure(0, weight=1)  # Equal weight for both frames
row2_frame.grid_columnconfigure(1, weight=1)

# Terminal Frame
terminal_frame = ctk.CTkFrame(row2_frame)
terminal_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
terminal_frame.grid_rowconfigure(0, weight=1)  # Make terminal expand fully
terminal_frame.grid_columnconfigure(0, weight=1)

terminal_monitor = ctk.CTkTextbox(terminal_frame, wrap="word")
terminal_monitor.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

# Button Frame
button_frame = ctk.CTkFrame(row2_frame)
button_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

list_btn = ctk.CTkButton(button_frame, text="List Task", command=list_task)
list_btn.grid(row=0, column=0, padx=5, pady=5)

debug_btn = ctk.CTkButton(button_frame, text="Debug", command=debug_task)
debug_btn.grid(row=1, column=0, padx=5, pady=5)

task_btn = ctk.CTkButton(button_frame, text="Sent Task", command=send_task_file)
task_btn.grid(row=2, column=0, padx=5, pady=5)

delete_btn = ctk.CTkButton(button_frame, text="Delete Task")
delete_btn.grid(row=3, column=0, padx=5, pady=5)

clear_btn = ctk.CTkButton(button_frame, text="Clear Monitor", command=clear_monitor)
clear_btn.grid(row=4, column=0, padx=5, pady=5)

# Command Entry & Send Button (Disabled for now)
command_entry = ctk.CTkEntry(button_frame, placeholder_text="Enter UART Command")
# command_entry.grid(row=5, column=0, padx=5, pady=(10, 2))

send_command_btn = ctk.CTkButton(button_frame, text="Send", command=send_command, state="disabled")
# send_btn.grid(row=6, column=0, padx=5, pady=(2, 10))

root.mainloop()