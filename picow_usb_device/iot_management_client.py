import adafruit_requests
import ssl
import adafruit_hashlib as hashlib
import os

ignored_dirs = [
    ".fseventsd",
    "System Volume Information",
]
ignored_files = [
    ".metadata_never_index",
    ".Trashes",
    "boot_out.txt",
]


def disk_size_in_mb():
    fs_stat = os.statvfs('/')
    return fs_stat[0] * fs_stat[2] / 1024 / 1024


def free_space_in_mb():
    fs_stat = os.statvfs('/')
    return fs_stat[0] * fs_stat[3] / 1024 / 1024


def print_fs():
    _print_directory("/")


def _print_directory(path, tabs=0):
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " by"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            _print_directory(path + "/" + file, tabs + 1)


class IotManagementClient:

    def __init__(self, server_url, socket_pool, config_identifier, code_identifier = None, remove_files=False, hash_algo="md5"):
        self.socket_pool = socket_pool
        self.server_url = server_url
        self.config_identifier = config_identifier
        self.code_identifier = code_identifier
        if code_identifier is None:
            self.code_identifier = config_identifier
        self.hash_algo = hash_algo
        self.remove_files = remove_files  # If we should delete files no longer on the server
        self.request = adafruit_requests.Session(socket_pool, ssl.create_default_context())
        self.temp_extension = ".tmp"

    def update_config(self):
        files_on_device = self.find_all_files_on_device()
        self.log(f"Files on device: {files_on_device.values()}")
        self.log("")
        update_files = self.get_config_files_from_server()
        update_files.extend(self.get_code_files_from_server())
        self.log(f"Files from server: {update_files}")
        self.log("")

        to_update = []
        new_files = []
        same = []

        for server_file in update_files:
            if server_file["name"] in files_on_device:
                on_device = files_on_device.pop(server_file["name"])
                if server_file["checksum"] != on_device["checksum"]:
                    to_update.append(server_file)  # Do we want the line or just the name??
                else:
                    same.append(server_file)
            else:
                new_files.append(server_file)
        self.log("")
        self.log(f"To remove: {files_on_device.values()}")
        self.log(f"To update: {to_update}")
        self.log(f"New: {new_files}")
        self.log(f"Same: {same}")

    def get_config_files_from_server(self):
        url = f"{self.server_url}/config/{self.config_identifier}"
        return self._get_file_list_from_server(url)

    def get_code_files_from_server(self):
        url = f"{self.server_url}/src/{self.code_identifier}"
        return self._get_file_list_from_server(url)

    def _get_file_list_from_server(self, url):
        resp = self.request.get(url)
        data = resp.json()
        resp.close()
        return data

    def download_config_file(self, file_name):
        url = f"{self.server_url}/src/{self.config_identifier}{file_name}"
        self._download_file(file_name, url)

    def download_code_file(self, file_name):
        url = f"{self.server_url}/src/{self.code_identifier}{file_name}"
        self._download_file(file_name, url)

    def _download_file(self, file_name, url):
        resp = self.request.get(url)
        temporary_filename = f"{file_name}{self.temp_extension}"
        with open(temporary_filename, "wb") as fp:
            self.log(dir(fp))
            fp.write(resp.content)
            fp.flush()
        resp.close()

        temp_hash = self._hash_for_file(temporary_filename)
        orig_hash = self._hash_for_file(file_name)
        self.log(f"{temp_hash == orig_hash}, {temp_hash}, {orig_hash}")

    def _replace_file(self, filename):
        # TODO replace an existing file with hash check and move
        pass

    def _add_new_file(self, filename):
        # TODO download new file and hash check it
        pass

    def _hash_for_file(self, file_name):
        file_hash = None
        with open(file_name, 'rb') as f:
            data = f.read()
            if self.hash_algo == "md5":
                file_hash = hashlib.md5(data).hexdigest()
            elif self.hash_algo == "sha256":
                file_hash = hashlib.sha256(data).hexdigest()
            elif self.hash_algo == "sha512":
                file_hash = hashlib.sha512(data).hexdigest()
        return file_hash

    def find_all_files_on_device(self):
        start_dir = ""
        map_of_files = {}
        files = self._find_files_on_device(start_dir, map_of_files, os.sep)
        return files

    def _find_files_on_device(self, path, map_of_files, path_sep):
        for file in os.listdir(path):
            file_path = f"{path}{path_sep}{file}"
            stats = os.stat(file_path)
            isdir = stats[0] & 0x4000

            # recursively print directory contents
            if isdir:
                if file not in ignored_dirs:
                    self._find_files_on_device(file_path, map_of_files, path_sep)
            else:
                if file not in ignored_files:
                    map_of_files[file_path[1:]] = {
                            # Removing the leading slash from all filenames
                            "name": file_path[1:],
                            # TODO it is fairly slow to hash all files on a drive - do we want to do this?
                            "checksum": self._hash_for_file(file_path),
                            "filesize": stats[6]
                    }
        return map_of_files

    def _log_to_server(self, message):
        url = f"{self.server_url}/log"
        resp = self.request.post(url, data=f'"{message}"')
        resp.close()

    def log(self, message):
        print(message)
        self._log_to_server(message)
