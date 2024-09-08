import array
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime

import numpy as np

from frontend.classes.analysisType import AnalysisType
from frontend.classes.file import File
from frontend.classes.project import Project


def get_md5(file_md5_hash: str, owner_id: str, analysis_type: str, list_var: str, selected_params: dict) -> str:
    str2hash = (file_md5_hash + owner_id + analysis_type + list_var + json.dumps(selected_params))
    return hashlib.md5(str2hash.encode()).hexdigest()

class CustomJSONizer(json.JSONEncoder):
    def default(self, obj):
        return super().encode(bool(obj)) \
            if isinstance(obj, np.bool_) \
            else super().default(obj)

@dataclass
class Analysis:
    file_md5_hash: str
    owner_id: str
    analysis_type: str
    md5_hash: str
    list_var: str
    selected_params: dict
    unconditioned: str
    conditioned: str
    hazard: str
    created_at: datetime

    def __init__(self, md5_hash: str, owner_id: str, analysis_type: AnalysisType, list_var: array,
                 selected_params: dict):
        self.file_md5_hash = md5_hash
        self.owner_id = owner_id
        self.analysis_type = analysis_type.value
        self.list_var = ','.join(str(x) for x in list_var)
        self.selected_params = selected_params
        self.unconditioned = ''
        self.conditioned = ''
        self.hazard = ''
        self.created_at = datetime.now()
        self.md5_hash = get_md5(self.file_md5_hash, self.owner_id, self.analysis_type, self.list_var,
                                self.selected_params)

    @staticmethod
    def dbInsert(analysis, db):
        db.insert("analysis", analysis)

    @staticmethod
    def analysisUpdate(md5_hash, results1, results2, results3, db):
        data = {
            'unconditioned': json.dumps(results1, cls=CustomJSONizer),
            'conditioned': json.dumps(results2, cls=CustomJSONizer),
            'hazard': json.dumps(results3, cls=CustomJSONizer),
        }
        db.update_one("analysis", {"md5_hash": md5_hash}, data)

        analysis = db.find("analysis", {"md5_hash": md5_hash})[0]
        project_id = File.get_project_id_by_file_md5_hash(analysis['file_md5_hash'], db)
        result = db.find("projects", {"uuid": project_id})[0]
        project = Project(result["name"], result["owner_id"], result["client_id"], result["analysis"],
                          result["created_at"], result["uuid"])
        project.add_analysis(md5_hash, db)

    @staticmethod
    def getAnalysis(sub, db):
        # define the keys to remove
        keys = ['_id', 'owner_id', 'file_md5_hash', 'unconditioned', 'conditioned', 'list_var']
        analysis = []
        pipeline = [
            {'$match': {'owner_id': sub, 'hazard':{'$ne': ''}}},
            {'$group': {'_id': '$file_md5_hash', "results": {"$push": "$$ROOT"}}},
            {'$project': {'_id': 0, 'owner_id': 0}}
        ]
        response = db.aggregate("analysis", pipeline)

        i = 0
        for results in response:
            for _, result in results.items():
                analysis.append({})
                for data in result:
                    if 'filename' not in analysis[len(analysis) - 1]:
                        file = db.find_one("files", {"md5_hash": data["file_md5_hash"]}, ('created_at', -1))
                        analysis[len(analysis) - 1]['filename'] = file["name"]
                        analysis[len(analysis) - 1]['analysis'] = []

                    for key in keys:
                        data.pop(key, None)

                    if 'created_at' in data:
                        data['created_at'] = data['created_at'].strftime("%Y-%m-%d %H:%M:%S")

                    if 'hazard' in data:
                        data['hazard'] = json.loads(data['hazard'])

                    analysis[len(analysis) - 1]['analysis'].append(data)
        return analysis

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True)

