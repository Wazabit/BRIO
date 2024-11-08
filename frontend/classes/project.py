import json
import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Project:
    id: str
    uuid: str
    name: str
    client_id: str
    owner_id: str
    analysis: [str]
    created_at: datetime

    def __init__(self, name: str, owner_id: str, client_id: str, analysis: str = '',
                 created_at: datetime = datetime.now(),
                 project_id: str = ''):
        self.name = name
        self.owner_id = owner_id
        self.client_id = client_id
        if type(analysis) == list:
            self.analysis = analysis
        else:
            self.analysis = analysis.split(',') if analysis != '' else []
        self.created_at = created_at
        if project_id == '':
            self.uuid = uuid.uuid4().hex[:16].lower()
        else:
            self.uuid = project_id

    @staticmethod
    def register_update(project, db):
        if len(db.find("projects", {"uuid": project.uuid})) == 0:
            db.insert("projects", project)
        else:
            db.update_one("projects", {"uuid": project.uuid}, project)

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)

    def add_analysis(self, analysis_id, db):
        self.analysis.append(analysis_id)
        db.update_one("projects", {"uuid": self.uuid}, self)
