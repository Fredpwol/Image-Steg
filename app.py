from main import io, app
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    io.run(app, port=5050)
