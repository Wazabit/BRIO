import hashlib
from dataclasses import dataclass
from datetime import datetime

from frontend.classes.fileStatus import FileStatus
from frontend.classes.fileType import FileType

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
    client_id: str
    project_id: str
    type: FileType
    md5_hash: str
    status: FileStatus
    created_at: datetime

    def __init__(self, filename: str, owner_id: str, filetype: FileType, filestatus: FileStatus, path: str, client_id: str, project_id: str):
        self.name = filename
        self.owner_id = owner_id
        self.type = filetype.value
        self.md5_hash = get_md5_hash(path, filename)
        self.status = filestatus.value
        self.created_at = datetime.now()
        self.client_id = client_id
        self.project_id = project_id

    def dbInsert(self, file, db):
        if len(db.find("files", {"md5_hash": file.md5_hash})) == 0:
            db.update_many("files", {"owner_id": file.owner_id}, {"status": FileStatus.USED.value})
            db.insert("files", file)
        else:
            db.update_many("files", {"owner_id": file.owner_id}, {"status": FileStatus.USED.value})
            db.update_one("files", {"md5_hash": file.md5_hash}, {"status": FileStatus.IN_USE.value})

    @staticmethod
    def get_project_id_by_file_md5_hash(file_md5_hash, db):
        result = db.find("files", {"md5_hash": file_md5_hash})[0]
        return result["project_id"]