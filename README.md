# Senior-Project-PC
This is my Senior Project on Embedded system

# AVR RTOS Task Manager & Compiler (PC Utility)

This is a Python-based utility designed to interact with a custom RTOS running on an ATMega328P microcontroller. It supports both serial communication (UART) and the compilation of C-based task files into RTOS-compatible binaries. The tool is intended for embedded developers looking to upload, manage, and monitor tasks on the RTOS system from a PC.

---

## 🔧 Features

### ✅ Serial Communication Interface
- Auto-detects available COM ports (FTDI232, USB-UART, etc.)
- Sends structured UART commands to the RTOS:
  - `<LIST>` — List all stored tasks
  - `<DEBUG>` — Dump raw EEPROM task content
  - `<DELETE:x>` — Delete specific task by ID
  - `<DELETE>` — Remove all stored tasks
- Reads and logs UART responses from the RTOS
- Compatible with Arduino Serial Monitor protocol

### 📦 Task File Upload (WIP)
- Upload `.bin` task files wrapped inside `<TASK:...>` markers
- Format includes:
  - Task Header (ID, Type, Priority, Size)
  - Task Binary Payload
- Currently fire-and-forget — will support checksums, retries, and confirmation in future updates

### 💻 GUI Interface (Planned via `customtkinter`)
- COM port selector
- Terminal output log with timestamps
- Task manager panel (planned)
- Memory visualization (planned)

---

## 🧠 Planned Compilation Toolchain
The utility will eventually compile custom user-defined AVR task code:

- Accepts AVR C source files (e.g., toggle LED, sensor read)
- Compiles using `avr-gcc` targeting `ATmega328P`
- Wraps output into a TaskHeader structure
- Sends combined binary via UART to the RTOS

---

## 📂 Repository Structure

```
.
├── .github/workflows/          # GitHub Actions (CI setup)
├── .gitignore                  # Standard Python ignore list
├── compiler.py                 # Main CLI script (serial & task upload)
├── requirement.txt             # Python dependencies
└── README.md                   # You're here!
```

---

## 📦 Installation

1. Clone this repository:
```bash
git clone https://github.com/Sirapobchon/Senior-Project-PC.git
cd Senior-Project-PC
```

2. Install Python requirements:
```bash
pip install -r requirement.txt
```

3. Run the CLI:
```bash
python compiler.py
```

---

## 🖥 Dependencies

- `pyserial` - Serial communication
- `customtkinter` - for GUI
- `subprocess` - Used for invoking `avr-gcc` (planned feature)
- `tkinter` - File dialogs and GUI elements

---

## ⚙️ Building Standalone Executable

Use PyInstaller to package into `.exe` (Windows):
```bash
pyinstaller --onefile compiler.py
```

---

## 📅 TODO

- [x] Basic UART communication
- [x] Task file upload via `<TASK:...>`
- [x] EEPROM debug and task list support
- [ ] GUI task manager interface
- [ ] Flash memory map visualization
- [ ] AVR code compiler with task builder
- [ ] CRC and upload verification system

---

## 🧑‍💻 Author

Developed by [Sirapobchon] & [PPPCYD] 
Part of the ATMega328P RTOS Development Project
