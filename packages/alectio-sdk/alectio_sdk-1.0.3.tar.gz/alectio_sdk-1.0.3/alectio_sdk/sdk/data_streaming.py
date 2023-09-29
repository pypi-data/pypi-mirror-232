import os
import json

# ----------------local imports----------------#
from .api_client import APIClient
from .gcp_storage import GCP_Storage
from .console import MainConsole

# ----------------frame works------------------#
import pandas as pd


class AnnotationStreaming:
    '''
    A class that returns the labels and annotations from the cloud bucket and creates a dataset.
    Returns datapoints along with the labels as numpy array.
    '''
    def __init__(self, token, root, indices) -> None:
        self.token = token
        self.root = root
        self.indices = indices
        self.console = MainConsole()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        
        with open(os.path.join(dir_path, "config.json"), "r") as f:
            self.config = json.load(f)
        
        self.api_client = APIClient(
            backend_url=self.config["backend_ip"], token=self.token)
        
        self.gcp_client = GCP_Storage(exp_token=token)


    def __pull_annotations(self):
        self.console.info("PULLING ANNOTATION FROM CLOUD")
        
        error, data = self.api_client.POST_REQUEST(
            end_point=f"/v2/get_annotation_data",
            payload={
                    "token": self.token,
                    "selected_indices": self.indices
                }
        )
        
        if error:
            self.console.error(
                "SOMETHING WENT WRONG WITH ALECTIO ANNOTATIONS LOADER.\nCONTACT ALECTIO ADMIN"
            )

        json_data = json.loads(data["data"]["dataframe"])
        dataframe = pd.DataFrame(json_data)

        if data["data"]["task_type"].lower() in ["object_detection", "image_classification"]:
            self.datapoints = dataframe['file_path'].to_list()
            self.annotations = dataframe['annotations'].to_list()
        elif data["data"]["task_type"].lower() == "text_classification":
            self.datapoints = dataframe['text'].to_list()
            self.annotations = dataframe['annotations'].to_list()
        else:
            raise Exception(f"{data['data']['task_type']} TASK TYPE IS NOT SUPPORTED YET")


    def get_dataset(self):
        self.__pull_annotations()
        return self.datapoints, self.annotations