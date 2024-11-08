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
                 projects: [str], created_at: datetime = datetime.now(),
                 client_id: str = ''):

        self.name = name
        self.contact = contact
        self.email = email
        self.logo = logo
        self.owner_id = owner_id
        if type(admins) == list:
            self.admins = admins
        else:
            self.admins = admins.split(',') if admins != '' else [owner_id]
        if type(editors) == list:
            self.editors = editors
        else:
            self.editors = editors.split(',') if editors != '' else []
        self.projects = projects
        self.created_at = created_at
        if client_id == '':
            self.uuid = uuid.uuid4().hex[:16].lower()
        else:
            self.uuid = client_id

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

    def add_project(self, project_id, db):
        self.projects.append(project_id)
        db.update_one("clients", {"uuid": self.uuid}, self)

    @staticmethod
    def get_client(client_id, db):
        result = db.find("clients", {"uuid": client_id})[0]
        client = Client(result["name"], result["contact"], result["email"], result["logo"], result["owner_id"],
                        result["admins"], result["editors"], result["projects"],
                        result["created_at"], result["uuid"])
        return client
