import uvicorn
import sys
from src.main import app
from src.core import settings

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "run":
            # Run the FastAPI application
            uvicorn.run(app, host="0.0.0.0", port=8000)
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: python main.py run")
    else:
        # Default: run the application
        uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()