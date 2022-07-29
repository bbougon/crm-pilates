from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
def health():
    return {"health": "OK"}
