import hashlib
from dataclasses import dataclass

from frontend.classes.fileType import FileType
from frontend.classes.user import User

BUF_SIZE = 65536


def get_md5_hash(path: str, filename: str) -> str:
    md5 = hashlib.md5()
    with open(path + '/' + filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()

@dataclass
class File:
    name: str
    owner_id: str
    type: FileType
    md5_hash: str

    def __init__(self, filename: str, owner_id: str, filetype: FileType, path: str):
        self.name = filename
        self.owner_id = owner_id
        self.type = filetype.value
        self.md5_hash = get_md5_hash(path, filename)

    def dbInsert(self, file, db):
        if len(db.find("files", {"md5_hash": file.md5_hash})) == 0:
            db.insert("files", file)
