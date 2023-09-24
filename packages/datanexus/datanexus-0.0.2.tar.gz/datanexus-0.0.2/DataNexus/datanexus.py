import requests
import os


class Datasets: 
    def __init__(self, path):
        self.path = path


    ## Datasets
    def possible_models(self):
        path = self.path

        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                print(file_path)

    ### Saving Datasets from DataNest
    def download_dataset_raw(url, save_path):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    file.write(response.content)

                print("Downloaded dataset")
                return "Downloaded dataset"
            
            else:
                print("Failed to download dataset")
                return "Failed to download dataset"
            
        except Exception as e:
            print(f'Error: {e}')
            return f"Error: {e}"

    
    def download_dataset(self, model):
        url = f"https://raw.githubusercontent.com/Ethan-Barr/DataNexus/main/Datanest/datasets/{model}"
        if not os.path.exists(model):
            Datasets.download_dataset_raw(url, model)
        else:
            return f"Local file '{model}' allready exists."


    ## Transcripts
    def load_whole_transcript(self, model):
        path = self.path

        if ".txt" in model:
            for file_name in os.listdir(path):
                if file_name == model:
                    target_file_path = os.path.join(path, model)
                    with open(target_file_path, 'r') as file:
                        file_contents = file.read()
                    return file_contents
            else:
                return "File not found in the specified folder."

    
    ## Character's
    def save_character(model, output_dir, character):
        lines = []
    
        with open(f"{model}", 'r') as source_flie:
            for line in source_flie:
                if character in line:
                    lines.append(line)
    
        if lines:
            with open(f"Characters/{output_dir}", 'w') as output:
                for line in lines:
                    output.write(line)
                    return f"{character} saved in {output}"


    def load_character(dataset):
        data = []
    
        with open(f"Characters/{dataset}", 'r') as source_file:
            for line in source_file:
                data.append(line)
    
        return data