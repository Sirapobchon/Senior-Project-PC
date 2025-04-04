import subprocess
import os
import platform

def compile_task_file(c_path, output_dir=None):
    if platform.system() == "Linux":
        avr_gcc_path = "/usr/bin/avr-gcc"
    else:
        avr_gcc_path = "C:/avr-gcc-14.1.0-x64-windows/bin/avr-gcc.exe"

    base_name = os.path.splitext(os.path.basename(c_path))[0]
    output_dir = output_dir or os.path.dirname(c_path)
    obj_file = os.path.join(output_dir, base_name + ".o")
    bin_file = os.path.join(output_dir, base_name + ".bin")

    # Step 1: Compile .c to .o (no linking)
    compile_cmd = [
        avr_gcc_path,
        "-mmcu=atmega328p",
        "-Os",
        "-c",            # Compile only, no linking
        "-o", obj_file,
        c_path
    ]

    # Step 2: Convert .o to .bin using objcopy
    objcopy_path = avr_gcc_path.replace("avr-gcc.exe", "avr-objcopy.exe")
    objcopy_cmd = [
        objcopy_path,
        "-O", "binary",
        obj_file,
        bin_file
    ]

    result = subprocess.run(compile_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Compilation error:\n{result.stderr}")

    result = subprocess.run(objcopy_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Objcopy error:\n{result.stderr}")

    return bin_file
