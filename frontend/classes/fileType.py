from enum import Enum


# class syntax
class FileType(Enum):
    DATASET = "dataset"
    MODEL = "model"
    DATAFRAME = "dataframe"
    NOTEBOOK = "notebook"
    ARTIFACTS = "artifacts"
