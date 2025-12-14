# Gemini Desktop Controller

This project provides a "productized" version of a desktop agent script, allowing you to install and run it as a standalone Windows executable (.exe) without managing Python environments. The agent uses a UI for managing an API key, which is saved locally for convenience.

## Features

-   **Login Screen:** A simple UI to enter and save your Google Gemini API key.
-   **Standalone Executable:** Packaged as a single `.exe` file that works like a portable app.
-   **Human-like Mouse Control:** The agent uses a "stealth" mouse driver to mimic human-like mouse movements.
-   **Vision Agent:** The agent can see the screen, analyze it, and perform actions based on your instructions.

## Installation and Usage

1.  **Download the Executable:**
    -   Grab the latest `launcher.exe` from the `dist` directory.

2.  **Run the Application:**
    -   Double-click `launcher.exe` to start the agent.
    -   The first time you run it, a web interface will open, asking for your Google Gemini API key.

3.  **Enter API Key:**
    -   Enter your API key in the login screen. It will be saved locally for future sessions.

4.  **Control Your Desktop:**
    -   Once the key is validated, you can start giving instructions to the agent through the chat interface.

## Building from Source

If you want to build the executable from the source code, follow these steps:

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Build Script:**
    ```bash
    python build_exe.py
    ```
    -   This will create a `dist` folder containing `launcher.exe`.

## How It Works

-   **`desktop_agent_v2.py`:** The main script containing the application logic, including the UI and the vision agent.
-   **`build_exe.py`:** A script that uses PyInstaller to package the application into a single executable.
-   **`hook-streamlit.py`:** A hook file to handle Streamlit's packaging complexities with PyInstaller.
-   **`launcher.py`:** A wrapper script created by `build_exe.py` to serve as the entry point for the executable.
