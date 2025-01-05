import yaml
import argparse
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

def update_api_tool(api_tool_name):
    with open(CONFIG_FILE, "r") as file:
        config = yaml.safe_load(file)

    config["api_tool"]["name"] = api_tool_name

    with open(CONFIG_FILE, "w") as file:
        yaml.safe_dump(config, file)

    print(f"Updated api_tool name to '{api_tool_name}' in {CONFIG_FILE}.")

def main(api_tool_name):
    # Update the YAML configuration
    update_api_tool(api_tool_name)

    # Load the updated configuration
    config = load_config()

    # Uncomment below if needed to handle specific tools
    api_tool = config["api_tool"]["name"]
    print(f"Selected API tool: {api_tool}")

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
    parser = argparse.ArgumentParser(description="Run the main script with a specific API tool.")
    parser.add_argument(
        "api_tool",
        type=str,
        help="The name of the API tool to use (e.g., openai, clc, ggVision, kandi, gemini)."
    )

    args = parser.parse_args()
    main(args.api_tool)
