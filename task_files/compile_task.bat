@echo off
setlocal EnableDelayedExpansion

REM Get file name and path
set "INPUT=%~1"
set "FILENAME=%~n1"
set "OBJFILE=%FILENAME%.o"
set "BINFILE=%FILENAME%.bin"
set "DEFAULT_FCPU=8000000UL"

echo Compiling "%INPUT%"...

REM Try to extract F_CPU from the file
set FCPU_FOUND=false
for /f "tokens=1,2,3 delims= " %%A in ('findstr /R /C:"#define F_CPU " "%INPUT%"') do (
    set "FCPU=%%C"
    set "FCPU_FOUND=true"
)

if "!FCPU_FOUND!"=="true" (
    echo Detected F_CPU from source: !FCPU!
) else (
    set "FCPU=%DEFAULT_FCPU%"
    echo Using default F_CPU=!FCPU!
)

REM Compile to .o object file (no linking)
avr-gcc -c -Os -DF_CPU=!FCPU! -mmcu=atmega328p -o "!OBJFILE!" "%INPUT%"
if errorlevel 1 goto :error

REM Convert .o to .bin directly
avr-objcopy -O binary -R .eeprom "!OBJFILE!" "!BINFILE!"

echo Done!
echo Output: "!BINFILE!"
pause
goto :eof

:error
echo Compilation failed.
pause
