# LiveKit Example Setup

This guide provides step-by-step instructions to set up and run the LiveKit example project.

## 1. Navigate to the Project Directory

Change to the `livekit_example` directory:
```bash
cd livekit_example
2. Create and Activate a Virtual Environment
Create a virtual environment using Python's built-in venv:
bashCopypython3 -m venv venv
Activate the virtual environment:
On macOS/Linux:
bashCopysource venv/bin/activate
On Windows:
bashCopyvenv\Scripts\activate
3. Install Python Dependencies
Install the required Python packages using pip:
bashCopypip install -r requirements.txt
4. Set Up Environment Variables
Create a file named .env.local in the project root directory and add the following environment variables. Replace the empty values with your actual keys and URL:
CopyLIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
LIVEKIT_URL=
DEEPGRAM_API_KEY=
OPENAI_API_KEY=
5. Install the Plugin
Make the installation script executable and then run it:
bashCopychmod +x install_plugin.sh
./install_plugin.sh
6. Run the Application
Start the application in development mode:
bashCopypython3 minimal_assistant.py dev
