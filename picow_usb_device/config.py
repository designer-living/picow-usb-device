DEFAULT_CONFIG = {
    "USB_ENABLED": True,
    "SOCKET_SERVER_ENABLED": True,
    "HTTP_SERVER_ENABLED": True,
    "HTTP_SERVER_PORT": 80,
    "ADMIN_SERVER_ENABLED": True,
    "ADMIN_SERVER_PORT": 5001,
    "PORT": 5000,
    "HOSTNAME": "myhostname",
    # Suggest this is disabled if connecting to a computer and
    # reading/writing code files over USB as I saw a lot of
    # watchdog restarts when doing this that corrupted some files.
    "WATCHDOG_ENABLED": False
}


def get_config_or_default(key, config):
    return config.get(key, DEFAULT_CONFIG.get(key))
