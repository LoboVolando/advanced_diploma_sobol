import uvicorn
from settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "application.src.app:app",
        reload=True,
        host=settings.host,
        port=settings.port,
    )
