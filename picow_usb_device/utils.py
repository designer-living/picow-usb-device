import storage


# safemode.py & boot.py file write
def precode_file_write(file, data):
    storage.remount("/", False)  # writeable by CircuitPython
    with open(file, "w") as fp:
        fp.write(f"{data}\n")
        fp.flush()
    storage.remount("/", True)   # writeable by USB host