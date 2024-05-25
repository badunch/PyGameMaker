import os
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any, List
import google.generativeai as genai
from google.api_core import exceptions, retry

# Load environment variables from .env file
load_dotenv()

# Configure the API key from the environment variable
GOOGLE_API_KEY = "AIzaSyDo8SD41dAhRB62tp48vDz2f1QDBe8gsH0"
if not GOOGLE_API_KEY:
    raise ValueError("API key not found. Ensure that the .env file contains the 'GOOGLE_API_KEY' variable.")
genai.configure(api_key=GOOGLE_API_KEY)

# Define the models with descriptions
MODELS: Dict[str, Dict[str, Any]] = {
    "gemini-1.5-flash-latest": {
        "model": genai.GenerativeModel("gemini-1.5-flash-latest"),
        "description": "Powerful model capable of handling text and image inputs, optimized for various language tasks like code generation, text editing, and problem solving.",
        "rate_limit": (15, 60),  # 2 queries per minute
        "daily_limit": 1000,
    },
    "gemini-1.0-pro-latest": {
        "model": genai.GenerativeModel("gemini-1.0-pro-latest"),
        "description": "Versatile model for text generation and multi-turn conversations, suitable for zero-shot, one-shot, and few-shot tasks.",
        "rate_limit": (60, 60),  # 60 queries per minute
    },
    "gemini-1.5-pro-latest": {
        "model": genai.GenerativeModel("gemini-1.5-pro-latest"),
        "description": "Versatile model for text generation and multi-turn conversations, suitable for zero-shot, one-shot, and few-shot tasks.",
        "rate_limit": (2, 60),  # 60 queries per minute
    },
}

@retry.Retry(
    initial=0.1,
    maximum=60.0,
    multiplier=2.0,
    deadline=600.0,
    exceptions=(exceptions.GoogleAPICallError,),
)
def generate_with_retry(model: genai.GenerativeModel, prompt: str) -> Any:
    try:
        return model.generate_content(prompt)
    except exceptions.InvalidArgument as e:
        raise ValueError(f"Invalid input provided: {e}")
    except exceptions.DeadlineExceeded as e:
        raise exceptions.DeadlineExceeded(f"Deadline exceeded while generating content: {e}")
    except exceptions.ResourceExhausted as e:
        raise exceptions.ResourceExhausted(f"Resource exhausted (quota limit reached): {e}")

def sanitize_title(title: str) -> str:
    sanitized_title = re.sub(r"[^\w\-_\. ]", "_", title)
    return sanitized_title[:100]

def load_text_file(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read().strip()

def extract_text(response: Any) -> str:
    for part in response.parts:
        if hasattr(part, "text"):
            return part.text
    return ""

def create_game_directory() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    game_dir = f"game_{timestamp}"
    os.makedirs(game_dir, exist_ok=True)
    return game_dir

def generate_game_prompt(draft: str, component: str) -> str:
    return (
        f"Generate the next part of the Python game."
        f"Here is the code generated so far:\n\n"
        f"{draft}\n\n"
        f"Now generate the code for the following component:\n\n"
        f"{component}\n"
    )

def ask_user_for_game_type() -> str:
    game_type = input("Enter the type of game you want to build (e.g., platformer, RPG, shooter): ").strip()
    return game_type

def generate_game_guide(model: genai.GenerativeModel, game_type: str) -> str:
    prompt = (
        f"Generate a detailed step-by-step guide on how to build a {game_type} game in Python. "
        f"Include the necessary components and explain each step in detail."
    )
    response = generate_with_retry(model, prompt)
    return extract_text(response)

def write_game_code(model_name: str, game_type: str, game_guide: str) -> None:
    model_config = MODELS[model_name]
    model = model_config["model"]
    rate_limit = model_config.get("rate_limit")
    daily_limit = model_config.get("daily_limit")

    # Extract game components from the guide
    game_components = game_guide.split("\n\n")
    
    # Create a directory for the game and its parts
    game_dir = create_game_directory()

    draft = ""
    query_count = 0
    max_iterations = 150

    for i, component in enumerate(game_components):
        print(f"Generating component {i + 1} out of {len(game_components)}...")
        if query_count >= max_iterations:
            break

        game_prompt = generate_game_prompt(draft, component)
        continuation = extract_text(generate_with_retry(model, game_prompt))
        draft += "\n\n" + continuation

        # Save each component's code
        component_filename = f"{game_dir}/component_{i + 1}.py"
        with open(component_filename, "w", encoding="utf-8") as file:
            file.write(continuation)

        query_count += 1

        if rate_limit and query_count % rate_limit[0] == 0:
            time.sleep(rate_limit[1])

        if daily_limit and query_count >= daily_limit:
            print("Daily query limit reached. Please try again tomorrow.")
            break

    final_code = draft.strip()
    print("Final Game Code:")
    print(final_code)

    final_filename = f"{game_dir}/{sanitize_title(game_type)}_game.py"
    with open(final_filename, "w", encoding="utf-8") as file:
        file.write(final_code)
    print(f"Final game code saved to {final_filename}")

    metadata_filename = f"{game_dir}/metadata.txt"
    with open(metadata_filename, "w", encoding="utf-8") as file:
        file.write("Generated game components:\n")
        file.write('\n'.join(game_components))
    print(f"Game components saved to {metadata_filename}")

def select_model() -> str:
    print("Available models:")
    for i, (model_name, model_info) in enumerate(MODELS.items(), start=1):
        print(f"{i}. {model_name} - {model_info['description']}")

    while True:
        try:
            choice = int(input("Enter the number corresponding to the model you want to use: "))
            if 1 <= choice <= len(MODELS):
                return list(MODELS.keys())[choice - 1]
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    selected_model = select_model()
    game_type = ask_user_for_game_type()
    game_guide = generate_game_guide(MODELS[selected_model]["model"], game_type)
    print(f"Generated guide for building a {game_type} game:\n{game_guide}")
    write_game_code(selected_model, game_type, game_guide)
