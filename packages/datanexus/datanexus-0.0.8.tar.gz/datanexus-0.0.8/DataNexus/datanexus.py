import requests
import os


class datanexus:
    # Datasets
    def models():
        api_url = 'https://api.github.com/repos/Ethan-Barr/DataNexus/contents/DataNexus/datasets'
        try:
            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()

                if isinstance(data, list):
                    model_list = [item['name'] for item in data]
                    for model in model_list:
                        return model_list
                else:
                    return []

            else:
                print(
                    f"Failed to retrieve content from {api_url}. Status code: {response.status_code}")
                return []

        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    # Saving Datasets from DataNexus

    @staticmethod
    def download_dataset_raw(url, save_path):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    file.write(response.content)
                return "Downloaded dataset"
            else:
                return "Failed to download dataset"

        except Exception as e:
            return f"Error: {e}"

    def download_dataset(self, model):
        url = f"https://raw.githubusercontent.com/Ethan-Barr/DataNexus/main/DataNexus/datasets/{model}"
        if not os.path.exists(model):
            self.download_dataset_raw(url, model)
        else:
            return f"Local file '{model}' allready exists."

    # Transcripts

    def load_whole_transcript(model):
        url = f"https://raw.githubusercontent.com/Ethan-Barr/DataNexus/main/DataNexus/datasets/{model}"

        try:
            response = requests.get(url)

            if response.status_code == 200:
                return response.text

            else:
                return "Failed to retrieve data"

        except Exception as e:
            return f"Error: {e}"

    # Character's

    def save_character(model, character, output_file):
        lines = []

        with open(f"{model}", 'r') as source_flie:
            for line in source_flie:
                if character in line:
                    lines.append(line)

        if lines:
            with open(f"Models/{output_file}", 'w') as output:
                for line in lines:
                    output.write(line)
            return f"{character} saved in {output}"

    def load_character(dataset):
        data = []

        with open(f"Models/{dataset}", 'r') as source_file:
            for line in source_file:
                data.append(line)

        return data