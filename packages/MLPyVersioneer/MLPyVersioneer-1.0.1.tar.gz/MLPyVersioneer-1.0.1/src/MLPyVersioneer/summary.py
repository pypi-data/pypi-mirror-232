from torch import nn
from torchinfo import summary
import os
import re

from exporter import Exporter

SUMMARY_FOLDER = "summaries"

class Summary:

    def __init__(self, model, ) -> None:
        self.model = model
        self.exporter = Exporter()
        self.version = self.calculate_version()


        if isinstance(model, nn.Module):
            self.meta_data = summary(model, verbose=0)


    
    def export(self) -> None:
        
        self.exporter.generate_folders()

        self.exporter.generate_files(self)

    def calculate_version(self) -> int:
        # get all the files in the summaries folder
        try:
            files = os.listdir(SUMMARY_FOLDER)

        except FileNotFoundError:
            return 1

        # get all the versions from the files
        versions = [int(re.findall(r'\d+', file)[0]) for file in files]

        # if there are no files, start at version 1
        if len(versions) == 0:
            return 1

        # get the latest version
        version = max(versions)

        # increment the version
        version += 1

        return version
    
        

        
        



        





