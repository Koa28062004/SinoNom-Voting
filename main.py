import yaml
import os 
from genGeminiLabel import run_gemini
from genGPTLabel import run_openai
from genCLCLabel import run_clc
from genGGVisionLabel import run_ggvision
from genKandiLabel import run_kandi
from voting import run_voting

CONFIG_FILE = "apiConfig.yaml"

def load_config():
    with open(CONFIG_FILE, "r") as file:
        return yaml.safe_load(file)
    
def main():
    config = load_config()
    run_voting(config)
    # api_tool = config["api_tool"]["name"]
    # print(f"Selected API tool: {api_tool}")

    # # Determine which API processing function to run
    # if api_tool == "openai":
    #     run_openai(config)
    # elif api_tool == "clc":
    #     run_clc(config)
    # elif api_tool == "ggVision":
    #     run_ggvision(config)
    # elif api_tool == "kandi":
    #     run_kandi(config)
    # elif api_tool == "gemini":
    #     run_gemini(config)
    # else:
    #     print(f"Unknown API tool: {api_tool}")

if __name__ == "__main__":
    main()