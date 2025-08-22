import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from yourapi import create_app

# Get the environment from the .env file, default to 'development'
env_name = os.getenv('FLASK_ENV', 'development')
app = create_app(env_name)

if __name__ == '__main__':
    # The host is set to '0.0.0.0' to be accessible from outside the container
    app.run(host='0.0.0.0')
