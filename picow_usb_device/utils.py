import storage
import supervisor
import microcontroller


NVM_INDEX_SAFEMODE = 0
SAFEMODECLEAR = 0
SAFEMODESET = 1


# safemode.py & boot.py file write
def precode_file_write(file, data):
    storage.remount("/", False)  # writeable by CircuitPython
    with open(file, "w") as fp:
        fp.write(f"{data}\n")
        fp.flush()
    storage.remount("/", True)   # writeable by USB host


def create_boot_dict():
    # update_restart_dict_time(boot_dict)  # add timestamp
    return {
        "reset_reason": str(microcontroller.cpu.reset_reason)

    }


def create_safe_mode_dict():
    # update_restart_dict_time(safemode_dict)  # add timestamp
    return {
        "safemode_reason": str(supervisor.runtime.safe_mode_reason)
    }


def create_run_dict():
    return {
        "run_reason": str(supervisor.runtime.run_reason),
        "previous_traceback": supervisor.get_previous_traceback()
    }
