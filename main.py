import yaml
import os 
import run_gemini
import run_openai
import run_clc
import run_ggvision
import run_kandi

CONFIG_FILE = "apiConfig.yaml"

def load_config():
    with open(CONFIG_FILE, "r") as file:
        return yaml.safe_load(file)
    
def main():
    config = load_config()
    
    api_tool = config["api_tool"]["name"]
    print(f"Selected API tool: {api_tool}")

    # Determine which API processing function to run
    if api_tool == "openai":
        run_openai(config)
    elif api_tool == "clc":
        run_clc(config)
    elif api_tool == "ggVision":
        run_ggvision(config)
    elif api_tool == "kandi":
        run_kandi(config)
    elif api_tool == "gemini":
        run_gemini(config)
    else:
        print(f"Unknown API tool: {api_tool}")

if __name__ == "__main__":
    main()