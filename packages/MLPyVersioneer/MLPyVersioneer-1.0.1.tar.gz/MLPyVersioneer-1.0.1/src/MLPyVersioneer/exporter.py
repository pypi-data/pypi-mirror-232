import os
import sys
import torch


SUMMARY_FOLDER = "summaries"
MODEL_FOLDER = "models"

ALL_FOLDERS = [SUMMARY_FOLDER, MODEL_FOLDER]

class Exporter:

    def __init__(self) -> None:

        pass
        

    def generate_folders(self) -> None:
        try:
            for folder in ALL_FOLDERS:
                if not os.path.exists(folder):
                    os.makedirs(folder)
        except:
            print("Error: Could not create folders")
            sys.exit(1)


    def generate_files(self, summary) -> None:

        # write the meta data to a file
        with open(f"{SUMMARY_FOLDER}/summary_{summary.version}.txt", "w") as f:
            f.write(str(summary.meta_data))

        # save the model
        torch.save(summary.model, f"{MODEL_FOLDER}/model_{summary.version}.pt")



        


