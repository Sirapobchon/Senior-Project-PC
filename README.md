# Senior-Project-PC
This is my Senior Project on Embedded system
It serves as a communication bridge and task compiler for a custom RTOS running on an **ATMega328P** microcontroller.

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
- Built-in Arduino Serial Monitor–like terminal
- Clean UI logs + separate debug monitor

### 📦 Task File Upload (WIP)
- Upload `.bin` task files wrapped inside `<TASK:...>` markers
- Adds structured **TaskHeader** before payload:
  - Task Header (ID, Type, Priority, Size, Status, FlashAddress)
  - Task Binary Payload
- Currently fire-and-forget — will support checksums, retries, and confirmation in future updates

### 💻 GUI Interface (WIP)
- Built with `customtkinter`
- COM port selector
- Terminal output log with timestamps
- Button controls for:
  - Task listing
  - EEPROM debug
  - Upload `.bin` file
  - Clear monitor
- Task manager panel (planned)
- Memory visualization (planned)

---

## ⚙️ Task Compilation via Batch Script (`Task_files/compile_task.bat`)
To compile your custom AVR task written in C, use the included batch file:
```
.
├── Task_files/
│   ├── compile_task.bat        # Drag-n-drop .c → .bin converter
```

- Accepts AVR C source files (e.g., toggle LED, sensor read)
- Compiles using `avr-gcc` targeting `ATmega328P`
- Save the .bin to be use in the python side (WIP to be merge with the python)

### 🔨 Requirements:
- Install [`avr-gcc`](https://github.com/avrdudes/avr-gcc-builds/releases)
- Add to your Windows PATH (e.g., `C:\avr-gcc-14.1.0-x64-windows\bin`)

### 📄 Usage:
- Write a `.c` file containing a `void task(void)` function
- Drag-and-drop your `.c` file onto `compile_task.bat`
- Generates `.hex`, `.elf`, and `.bin` files

---

## 📂 Repository Structure

```
.
├── .github/workflows/          # GitHub Actions (CI setup)
├── .gitignore                  # Standard Python ignore list
├── Task_files/
│   ├── compile_task.bat        # Drag-n-drop .c → .bin converter
│   └── readme.txt              # Info about batch compile usage
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
- `tkinter` - File dialogs and GUI elements
- `customtkinter` - for GUI library
- `subprocess` - Used for invoking `avr-gcc` compile integration (planned feature)

---

## ⚙️ Building Standalone Executable

Use PyInstaller to package into `.exe` (Windows):
```bash
pyinstaller --onefile compiler.py
```

---

## 📅 TODO

- [x] Basic UART communication
- [x] EEPROM debug and task list support
- [x] Binary task upload via GUI
- [x] AVR code compiler (.c → .bin via .bat)
- [ ] GUI task manager interface
- [ ] Flash memory map visualization
- [ ] CRC and upload verification system

---

## 🧑‍💻 Author

Developed by [Sirapobchon] & [PPPCYD] 
Part of the ATMega328P RTOS Development Project
