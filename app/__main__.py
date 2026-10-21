import os

from dotenv import load_dotenv

from .web import create_app

load_dotenv()
application = create_app()

if __name__ == "__main__":
    application.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        debug=False,
    )

