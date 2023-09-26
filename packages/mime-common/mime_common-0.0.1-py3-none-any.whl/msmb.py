
from __future__ import annotations
import socket
from smb.SMBConnection import SMBConnection
from smb.base import SharedFile, SharedDevice
from smb.smb_structs import OperationFailure, ProtocolError, UnsupportedFeature
from smb.base import SMBTimeout, NotReadyError, NotConnectedError
import io
import os
from plib.logg import Logg

class FileAttr:
    ATTR_READONLY = 0x00000001
    ATTR_HIDDEN = 0x00000002
    ATTR_SYSTEM = 0x00000004
    ATTR_DIRECTORY = 0x00000010
    ATTR_ARCHIVE = 0x00000020
    ATTR_NORMAL = 0x00000080
    ATTR_TEMPORARY = 0x00000100
    ATTR_COMPRESSED = 0x00000800
    POSIX_SEMANTICS = 0x01000000
    BACKUP_SEMANTICS = 0x02000000
    DELETE_ON_CLOSE = 0x04000000
    SEQUENTIAL_SCAN = 0x08000000
    RANDOM_ACCESS = 0x10000000
    NO_BUFFERING = 0x20000000
    WRITE_THROUGH = 0x80000000

    POWER_LABELS: dict[int, str] = {
        0: ' b',
        1: ' k',
        2: ' M',
        3: ' G',
        4: ' T',
        5: ' E',
    }

    @staticmethod
    def check(value, attribute) -> bool:
        return bool(value&attribute)
    
    @staticmethod
    def attribute_string(value) -> str:
        attr: str = 'r' if bool(value&FileAttr.ATTR_READONLY) else '-'
        attr += 'h' if bool(value&FileAttr.ATTR_HIDDEN) else '-'
        attr += 's' if bool(value&FileAttr.ATTR_SYSTEM) else '-'
        attr += 'd' if bool(value&FileAttr.ATTR_DIRECTORY) else '-'
        attr += 'z' if bool(value&FileAttr.ATTR_COMPRESSED) else '-'
        return attr

    @staticmethod
    def format_bytes(size, precision=0) -> float:
        power: int = 2**10 # =1024
        n = 0
        while size > power:
            size /= power
            n += 1
        return f"{size:.{precision}f}{FileAttr.POWER_LABELS[n]}"


class File:
    def __init__(self, shared_file: SharedFile):
        self.shared_file = shared_file
    @property
    def create_time(self):
        return self.shared_file.create_time

    @property
    def name(self):
        return self.shared_file.filename

    @property
    def file_size(self):
        return self.shared_file.file_size

class Directory(File):
    def __init__(self, shared_file: SharedFile, file_list: dict = None):
        self.file_list = []
        if file_list is not None:
            self.file_list = file_list
        super().__init__(shared_file)

    def add_file(self, file:File):
        self.file_list.append(file)

class mSMB:
    """
    Class for SMB operations
    """

    TCP_PORT = '445'
    DEFAULT_LOGG = "plib.msmb.log"
    DEFAULT_LOGG_LEVEL: int = Logg.DEBUG
    COMMENT_CHAR = '#'

    def __init__(self, username: str, password: str, server_name: str, domain: str, stdignore: str = '.stdignore', logg:Logg=None, mandatory_stdignore=True) -> None:
        """
        Initialize a SMB connection

        :param str username: Username connecting to SMB server
        :param str password: Password of user
        :param str server_name: Server we're connecting to
        :param str domain: domain for SMB authentication
        """
        self.username: str = username
        self.password: str = password
        self.server_name: str = server_name
        self.domain: str = domain
        self.stdignore: str = stdignore
        self.mandatory_stdignore: bool = mandatory_stdignore
        self.server_ip: str = socket.gethostbyname(self.server_name)
        self.hostname: str = socket.gethostname()
        self.l: Logg = Logg(filename=self.DEFAULT_LOGG, level=self.DEFAULT_LOGG_LEVEL) if logg is None else logg

        self.connect()
        # print(locale.locale_encoding_alias)
        # locale.setlocale(locale.LC_ALL, 'nb_NO.utf8')

    def __del__(self):
        if self.conn is not None:
            self.close()

    def close(self):
        self.conn.close()

    def connect(self):
        conn = SMBConnection(self.username, self.password, self.hostname, self.server_name, self.domain, use_ntlm_v2=True,
                        is_direct_tcp=True)
        conn.connect(self.server_ip, self.TCP_PORT)
        print("Trying to echo...")
        echo = "Hello Samba"
        pong = ""
        try:
            pong = conn.echo(echo)
        except:
            conn = None
        if pong == echo:
            print("Connection OK")
        else:
            print("CONNECTION FAILED")
        self.conn: SMBConnection | None = conn
        """Object containing smb connection to the SMB server"""

    def dir(self, share, folder) -> list:
        ret: list = []
        directory = self.conn.listPath(share, folder)
        sf: SharedFile
        for sf in directory:
            obj: dict = {}
            obj['name'] = sf.filename 
            obj['folder'] = sf.isDirectory
            size = int(sf.file_size)
            obj['size'] = FileAttr.format_bytes(size)
            obj['time'] = sf.create_time
            obj['attributes'] = FileAttr.attribute_string(sf.file_attributes)
            obj['hidden'] = FileAttr.check(int(sf.file_attributes), FileAttr.ATTR_HIDDEN)
            obj['compressed'] = FileAttr.check(int(sf.file_attributes), FileAttr.ATTR_COMPRESSED)
            obj['readonly'] = FileAttr.check(int(sf.file_attributes), FileAttr.ATTR_READONLY)
            obj['system'] = FileAttr.check(int(sf.file_attributes), FileAttr.ATTR_SYSTEM)
            ret.append(obj)
        return ret
    
    def get_file(self, share:str, filename:str, file_object) -> None:
        """
            get single file from SMB-share

            :param share: The name of the share containing the file
            :param filename: Path to file to get
            :param file_object: Reference to a File-Like object to write the filedata to
        """
        self.l.debug(f"Getting file ")
        try:
            self.conn.retrieveFile(share, filename, file_object)
        except OperationFailure as error:
            self.l.error(f"OperationFailure getting file {share}{filename}")
            self.l.error(f"{error.message}")
            self.l.debug(error.smb_messages)
            raise error
        except Exception as error:
            self.l.error(f"Exception getting file {share}{filename}")
            self.l.error(error)
            raise error


    def store_file(self, share:str, filename:str, file_object) -> None:
        """
            store single file to SMB-share

            :param share: The name of the share containing the file
            :param filename: Path to file to save
            :param file_object: Reference to a File-Like object containing filedata
        """
        self.l.debug(f"Storing file ")
        if self.exists(share, filename):
            self.delete(share, filename)

        try:
            self.conn.storeFile(share, filename, file_object)
        except OperationFailure as error:
            self.l.error(f"OperationFailure storing file {share}{filename}")
            self.l.error(f"{error.message}")
            self.l.debug(error.smb_messages)
            raise error
        except Exception as error:
            self.l.error(f"Exception storing file {share}{filename}")
            self.l.error(error)
            raise error


    def get_stdignore(self, share:str, folder) -> list:
        """
            get stdignore list from remote share

            :param share: The name of the share containing the file
            :param folder: Path to folder within share to check for stdignore-file
        """
        self.l.debug("get_stdignore...")
        ret: list = [] 
        ret.append(self.stdignore)

        mem_file = io.BytesIO()
        try:
            self.get_file(share, f"{os.path.join(folder, '')}{self.stdignore}", mem_file)
        except Exception as error:
            self.l.error(f"Exception getting stdignore {share}/{os.path.join(folder, '')}{self.stdignore}")
            self.l.error(error)
            if self.mandatory_stdignore:
                raise error
        else:
            mem_file.seek(0)
            string_file = io.TextIOWrapper(mem_file, encoding='utf-8')

            line: str = string_file.readline()
            while line:
                stripped: str = line.strip()
                if len(stripped) > 0:
                    first: str = stripped[0]
                    if first != self.COMMENT_CHAR:
                        ret.append(stripped)
                line = string_file.readline()
            string_file.close()
            mem_file.close()
        return ret

    def mkdir(self, share:str, folder:str, check_if_exists:bool=True):
        """Create a folder on share"""
        if check_if_exists:
            if self.exists(share, folder):
                raise FileExistsError(f"Unable to create Folder. '{folder}' already exists on share '{share}'")     
            # path_elements: tuple[str, str] = os.path.split(folder)
            # content: list = self.dir(share, path_elements[0])
            # for element in content:
            #     if element['name'] == path_elements[1]:
            #         # If already exists, no need to create
            #         raise FileExistsError(f"Unable to create Folder. '{folder}' already exists on share '{share}'")     

        try:
            self.conn.createDirectory(share, folder)
        except OperationFailure as error:
            self.l.warning(f"OperationFailure: {error.message} when creating folder {share}{os.path.join(folder, '')}")
            self.l.warning(error.message)
            [self.l.debug(smb_msg) for smb_msg in error.smb_messages]
            
            # self.l.warning(f"File already exists creating folder {share}/{os.path.join(folder, '')}")
        except Exception as error:
            self.l.error(f"Exception creating folder {share}/{os.path.join(folder, '')}")
            self.l.error(error)
            raise error

    def delete(self, share:str, file_pattern:str, folders:bool = False ) -> None:
        """
            delete files based on pattern

            :param share: The name of the share containing the file
            :param file_pattern: File pattern to delete. i.e.
        """
        self.l.debug(f"Deleting folder {file_pattern}")
        # TODO: Do some error handling here...
        self.conn.deleteFiles(share, file_pattern, folders)

    def deldir(self, share, folder):
        """
            delete single directory

            :param share: The name of the share containing the folder
            :param folder: Folder to delete. i.e.
        """
        self.l.debug(f"Deleting folder {folder}")
        self.conn.deleteDirectory(share, folder)
         

    def exists(self, share:str, path:str) -> bool:
        """CHeck if file/folder exists"""
        path_elements: tuple[str, str] = os.path.split(path)
        content: list = self.dir(share, path_elements[0])
        for element in content:
            if element['name'] == path_elements[1]:
                return True
        return False

