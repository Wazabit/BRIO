import json
from dataclasses import dataclass

from frontend.classes.client import Client
from frontend.classes.fileStatus import FileStatus
from frontend.classes.project import Project


@dataclass
class User:
    id: str
    name: str
    email: str
    picture: str
    sub: str
    max_result_views: int
    share_results: bool
    role: str

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
        if "role" in data["user_metadata"]:
            self.role = data["user_metadata"]["role"]
        else:
            self.role = "User"

    @staticmethod
    def register_update(user, db):
        if len(db.find("users", {"sub": user.sub})) == 0:
            db.insert("users", user)
            client = Client('Personal Client for ' + user.name, user.name, user.email, '', user.sub, user.sub, '', [])
            client.register_update(client, db)
            project = Project("Personal Project", user.sub, client.uuid)
            project.register_update(project, db)
            client.add_project(project.uuid, db)
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

    def get_users_by_role(self, db, role):
        return db.find("users", {"role": role})

    def get_my_clients(self, db):
        clients = []
        pipeline = [
            {'$match': {'$or': [{'admins': {"$in": [self.sub]}}, {'editors': {"$in": [self.sub]}}]}},
            {'$project': {'_id': 0}}
        ]

        response = db.aggregate("clients", pipeline)
        for results in response:
            results['tot_projects'] = len(results['projects'])
            projects = results['projects']
            results['projects'] = dict()

            for project in projects:
                project_data = db.find("projects", {"uuid": project})[0]
                if project_data is not None:
                    project_data['tot_analysis'] = len(project_data['analysis'])
                    project_data['created_at'] = project_data['created_at'].strftime("%a %d %b %Y")
                    results['projects'][project] = project_data

            clients.append(results)

        return clients
