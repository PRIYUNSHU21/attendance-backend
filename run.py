# Run the application
from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # Use environment variable for port (Railway requirement)
    port = int(os.environ.get("PORT", 5000))
    # Set debug=False for production
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(debug=debug, host="0.0.0.0", port=port)