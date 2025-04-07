# LiveKit Example Setup

This guide will help you set up the livekit_example project by creating a virtual environment, installing dependencies, configuring environment variables, and installing the necessary plugin.

## Prerequisites

- Python 3.x installed
- `virtualenv` or the built-in `venv` module available
- `pip` installed

## Setup Instructions

1. **Change Directory**

   Navigate to the project directory:
   ```bash
   cd livekit_example
Create and Activate a Virtual Environment

Create a virtual environment (using venv):

bash
Copy
Edit
python3 -m venv venv
Activate the virtual environment:

On macOS/Linux:

bash
Copy
Edit
source venv/bin/activate
On Windows:

bash
Copy
Edit
venv\Scripts\activate
Install Python Dependencies

Install the required packages using:

bash
Copy
Edit
pip install -r requirements.txt
Set Up Environment Variables

Create a file named .env.local in the project root with the following content:

dotenv
Copy
Edit
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=your_livekit_url
DEEPGRAM_API_KEY=your_deepgram_api_key
OPENAI_API_KEY=your_openai_api_key
Replace each placeholder (e.g., your_livekit_api_key) with your actual API keys and URL.

Install Plugin

Make the installation script executable and run it:

bash
Copy
Edit
chmod +x install_plugin.sh
./install_plugin.sh
Run the Application

Start the application in development mode:

bash
Copy
Edit
python3 minimal_assistant.py dev
Additional Notes
Ensure that your API keys and URLs are correct.

If you encounter any issues during setup, please consult the project's documentation or contact the maintainers for support.
