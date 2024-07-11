import array
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime

from frontend.classes.analysisType import AnalysisType
from ast import literal_eval


def get_md5(file_md5_hash: str, owner_id: str, analysis_type: str, list_var: str, selected_params: dict,
            created_at: str) -> str:
    str2hash = (file_md5_hash + owner_id + analysis_type + list_var + json.dumps(selected_params) + created_at)
    return hashlib.md5(str2hash.encode()).hexdigest()


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
                                self.selected_params, self.created_at.strftime("%Y-%m-%d %H:%M:%S"))

    @staticmethod
    def dbInsert(analysis, db):
        db.insert("analysis", analysis)

    @staticmethod
    def analysisUpdate(md5_hash, results1, results2, results3, db):
        conditioned = {}
        for key, value in results2.items():
            conditioned[key] = (repr(value).replace("(", "").replace(")", "")
                                .replace("[", "").replace("]", "")
                                .split(','))

        data = {
            'unconditioned': repr(results1).replace("(", "").replace(")", "")
            .replace("[", "").replace("]", "")
            .split(','),
            'conditioned': conditioned,
            'hazard': repr(results3).replace("[", "").replace("]", "").split(',')
        }
        db.update_one("analysis", {"md5_hash": md5_hash}, data)

    @staticmethod
    def getAnalysis(sub, db):
        # define the keys to remove
        keys = ['_id', 'owner_id', 'file_md5_hash', 'unconditioned', 'conditioned', 'list_var']
        analysis = []
        pipeline = [
            {'$match': {'owner_id': sub}},
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

                    analysis[len(analysis) - 1]['analysis'].append(data)
        return analysis

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True)
