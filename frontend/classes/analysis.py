import array
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime

from frontend.classes.analysisType import AnalysisType


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
    groups: str
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
        self.groups = ''
        self.conditioned = ''
        self.hazard = ''
        self.created_at = datetime.now()
        self.md5_hash = get_md5(self.file_md5_hash, self.owner_id, self.analysis_type, self.list_var,
                                self.selected_params, self.created_at.strftime("%Y-%m-%d %H:%M:%S"))

    @staticmethod
    def dbInsert(analysis, db):
        db.insert("analysis", analysis)

    @staticmethod
    def dbUpdate(md5_hash, data, db):
        db.update_one("analysis", {"md5_hash": md5_hash}, data)

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True)
