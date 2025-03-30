compile_task.bat - Simple AVR Task Compiler
-------------------------------------------

This batch file compiles a single C source file into a .bin binary,
suitable for uploading to the RTOS running on ATMega328P.

Requirements:
- avr-gcc must be installed and added to your Windows PATH.
  Example: C:\avr-gcc-14.1.0-x64-windows\bin

Usage:
- Drag and drop a .c file onto compile_task.bat
- Or run from command line:
    compile_task.bat yourfile.c

Output:
- yourfile.elf : compiled intermediate file
- yourfile.hex : HEX version (for flashing)
- yourfile.bin : raw binary for RTOS task upload

Notes:
- The C file must define a `void task(void)` function.
- Include F_CPU and proper AVR headers in the source.
- This script does NOT generate the TaskHeader – use the PC utility (compiler.py) to wrap it before sending.

Example task.c structure:
-------------------------
#define F_CPU 8000000UL
#include <avr/io.h>
#include <util/delay.h>

void task(void) {
    DDRB |= (1 << PB0);
    while (1) {
        PORTB ^= (1 << PB0);
        _delay_ms(500);
    }
}
