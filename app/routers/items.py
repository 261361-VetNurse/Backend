"""
Items Router - API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from app.services.item_service import ItemService
from app.database import get_database

router = APIRouter(
    prefix="/items",
    tags=["items"]
)


@router.get("/", response_model=List[ItemResponse])
async def get_all_items(db=Depends(get_database)):
    """ดึงข้อมูล items ทั้งหมด"""
    service = ItemService(db)
    return await service.get_all_items()


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str, db=Depends(get_database)):
    """ดึงข้อมูล item ตาม ID"""
    service = ItemService(db)
    item = await service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ไม่พบ item")
    return item


@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate, db=Depends(get_database)):
    """สร้าง item ใหม่"""
    service = ItemService(db)
    return await service.create_item(item)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, item: ItemUpdate, db=Depends(get_database)):
    """อัพเดท item"""
    service = ItemService(db)
    updated_item = await service.update_item(item_id, item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="ไม่พบ item")
    return updated_item


@router.delete("/{item_id}")
async def delete_item(item_id: str, db=Depends(get_database)):
    """ลบ item"""
    service = ItemService(db)
    deleted = await service.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="ไม่พบ item")
    return {"message": "ลบ item สำเร็จ"}
