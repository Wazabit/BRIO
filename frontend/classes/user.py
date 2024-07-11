import json
from dataclasses import dataclass

from frontend.classes.fileStatus import FileStatus


@dataclass
class User:
    id: str
    name: str
    email: str
    picture: str
    sub: str
    max_result_views: int
    share_results: bool

    def __init__(self, data):
        self.name = data["name"]
        self.email = data["email"]
        self.picture = data["picture"]
        self.sub = data["sub"]
        if "max_result_views" in data["user_metadata"]:
            self.max_result_views = data["user_metadata"]["max_result_views"]
        else:
            self.max_result_views = 0
        if "share_results" in data["user_metadata"]:
            self.share_results = data["user_metadata"]["share_results"]
        else:
            self.share_results = False

    @staticmethod
    def register_update(user, db):
        if len(db.find("users", {"sub": user.sub})) == 0:
            db.insert("users", user)
        else:
            db.update_one("users", {"sub": user.sub}, user)

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)

    def get_use_file(self, db):
        return db.find_one("files", {"owner_id": self.sub, "status": FileStatus.IN_USE.value}, ('created_at', -1))

    def update_all_status_files(self, db, status: FileStatus):
        db.update_many("files", {"owner_id": self.sub}, {"status": status.value})
