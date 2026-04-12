from fastapi import APIRouter

router = APIRouter(prefix="/metadata_inventory")


@router.get("/")
def startup():
    return {
        "status": 200,
        "message": "Successfull startup",
    }
