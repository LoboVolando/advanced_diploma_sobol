import uvicorn
from settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "api.app:app", reload=True, host=settings.host, port=settings.port
    )
