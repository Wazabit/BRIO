import json
import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Client:
    id: str
    uuid: str
    name: str
    contact: str
    email: str
    logo: str
    owner_id: str
    admins: [str]
    editors: [str]
    projects: [str]
    created_at: datetime

    def __init__(self, name: str, contact: str, email: str, logo: str, owner_id: str, admins: str, editors: str,
                 projects: [str]):
        self.name = name
        self.contact = contact
        self.email = email
        self.logo = logo
        self.owner_id = owner_id
        self.admins = admins.split(',') if admins != '' else []
        self.editors = editors.split(',') if editors != '' else []
        self.projects = projects
        self.created_at = datetime.now()
        self.uuid = str(uuid.uuid4().hex[:16].lower())

    @staticmethod
    def register_update(client, db):
        if len(db.find("clients", {"uuid": client.uuid})) == 0:
            db.insert("clients", client)
        else:
            db.update_one("clients", {"uuid": client.uuid}, client)

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)


