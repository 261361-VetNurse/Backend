"""
Pet Owners Main Router
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/pet-owners",
    tags=["Pet Owners"]
)


@router.get("")
async def pet_owners_root():
    """
    Root endpoint for Pet Owners
    """
    return {
        "message": "Pet Owners API",
        "endpoints": [
            "/pet-owners/home-page - Home page routes",
            "/pet-owners/profile - Profile management (coming soon)",
            "/pet-owners/settings - Settings (coming soon)"
        ]
    }
