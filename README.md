
## AI-Powered Python Game Generator

This Python script leverages Google GenerativeAI to assist you in creating Python games. It helps you design a game structure by providing step-by-step guidance and generating code for various components.

### Features

* **Model Selection:** Choose from different GenerativeAI models with varying capabilities and rate limits.
* **Game Type Input:** Specify the type of game you want to build (e.g., platformer, RPG, shooter).
* **Step-by-Step Guide Generation:** Get a detailed guide outlining the necessary components and their functionalities.
* **Code Generation for Components:** Generate Python code for each game component based on your prompts.
* **Organized File Structure:** Saves generated code in dedicated directories for easy management.
* **Rate Limiting and Quota Handling:** Implements safeguards to respect GenerativeAI's usage limits.

### Requirements

* Python 3.x
* Google GenerativeAI API (requires an API key)
* `dotenv` library (for managing environment variables)
* `google-api-python-client` library (for interacting with Google APIs)

### Installation

1. Install the required libraries using `pip`:

   ```bash
   pip install google-api-python-client dotenv
   ```

2. Obtain a Google GenerativeAI API key and create a `.env` file in your project directory with the following content:

   ```
   GOOGLE_API_KEY=YOUR_API_KEY_HERE
   ```

### Usage

1. Run the script:

   ```bash
   python game_generator.py
   ```

2. Follow the prompts to select a model, enter your desired game type, and collaborate with the script to generate the game's code.

### Example Output

The script will guide you through creating a game development plan, generate code for individual components, and organize them within a directory structure.

### Customization

* You can modify the `MODELS` dictionary to include additional GenerativeAI models with their descriptions and rate limits.
* The `generate_game_prompt` function can be adjusted to tailor prompts for specific game mechanics or functionalities.

### Disclaimer

* This script is provided for educational purposes only. Adhere to Google GenerativeAI's terms of service and responsible use guidelines.
* The quality and complexity of generated code may vary depending on the chosen model and provided prompts.

