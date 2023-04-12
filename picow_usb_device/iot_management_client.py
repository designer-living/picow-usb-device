import adafruit_requests
import ssl
import adafruit_hashlib as hashlib
import os


class IotManagementClient:

    def __init__(self, identifier, server_url, socket_pool, remove_files=False, hash_algo="md5"):
        self.socket_pool = socket_pool
        self.server_url = server_url
        self.identifier = identifier
        self.hash_algo = hash_algo
        self.remove_files = remove_files  # If we should delete files no longer on the server
        self.request = adafruit_requests.Session(socket_pool, ssl.create_default_context())
        self.temp_extension = ".tmp"

    def disk_size_in_mb(self):
        fs_stat = os.statvfs('/')
        return fs_stat[0] * fs_stat[2] / 1024 / 1024

    def free_space_in_mb(self):
        fs_stat = os.statvfs('/')
        return fs_stat[0] * fs_stat[3] / 1024 / 1024

    def update_config(self):
        files_on_device = self.find_all_files_on_device()
        print(files_on_device)
        update_files = self.get_config_files_from_server()
        update_files.extend(self.get_code_files_from_server())
        # TODO we have a leading / on file names from device.
        to_update = []
        new_files = []
        for file_line in update_files:
            print(f"FileLine: {file_line}")
            if file_line["name"] in files_on_device:
                files_on_device.remove(file_line["name"])
                if (not self.hashes_equal(file_line)):
                    to_update.append(file_line)  # Do we want the line or just the name??
            else:
                new_files.append(file_line)
        print(f"To remove: {files_on_device}")
        print(f"To update: {to_update}")
        print(f"New: {new_files}")

    def get_config_files_from_server(self):
        url = f"{self.server_url}/config/{self.identifier}"
        return self._get_file_list_from_server(url)

    def get_code_files_from_server(self):
        url = f"{self.server_url}/src/{self.identifier}"
        return self._get_file_list_from_server(url)

    def _get_file_list_from_server(self, url):
        resp = self.request.get(url)
        data = resp.json()
        print(data)
        return data

    def download_file(self, file_name):
        url = f"{self.server_url}/src/{self.identifier}{file_name}"
        resp = self.request.get(url)
        content = resp.content
        print(type(content))
        temporary_filename = f"{file_name}{self.temp_extension}"
        with open(temporary_filename, "wb") as fp:
            print(dir(fp))
            fp.write(f"{data}\n")
            fp.flush()
            # Check - checksum
        temp_hash = self._hash_for_file(temporary_filename)
        orig_hash = self._hash_for_file(file_name)
        print(temp_hash == orig_hash, temp_hash, orig_hash)

    def _replace_file(self, filename):
        # TODO replace an existing file with hash check and move
        pass

    def _add_new_file(self, filename):
        # TODO download new file and hash check it
        pass

    def hashes_equal(self, server_file):
        filename = server_file.get("name")
        server_checksum = server_file.get("checksum")
        try:
            our_checksum = self._hash_for_file(filename)
            return our_checksum == server_checksum
        except OSError as e:
            # Most liekly file not found - so count as needing to update
            print(e)
            return False

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
        list_of_files = []
        files = self._find_files_on_device(start_dir, list_of_files, os.sep)
        return files

    def _find_files_on_device(self, path, list_of_files, path_sep):
        for file in os.listdir(path):
            file_path = f"{path}{path_sep}{file}"
            stats = os.stat(file_path)
            isdir = stats[0] & 0x4000

            # recursively print directory contents
            if isdir:
                self._find_files_on_device(file_path, list_of_files, path_sep)
            else:
                list_of_files.append(file_path)
        return list_of_files

    def print_fs(self):
        self._print_directory("/")

    def _print_directory(self, path, tabs=0):
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
                self._print_directory(path + "/" + file, tabs + 1)