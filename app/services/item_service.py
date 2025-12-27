"""
Item Service - Business Logic
"""

from typing import List, Optional
from bson import ObjectId
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    """Service สำหรับจัดการ Items"""
    
    def __init__(self, database):
        self.collection = database["items"]
    
    async def get_all_items(self) -> List[dict]:
        """ดึงข้อมูล items ทั้งหมด"""
        items = await self.collection.find().to_list(length=100)
        return [self._format_item(item) for item in items]
    
    async def get_item_by_id(self, item_id: str) -> Optional[dict]:
        """ดึงข้อมูล item ตาม ID"""
        try:
            item = await self.collection.find_one({"_id": ObjectId(item_id)})
            return self._format_item(item) if item else None
        except:
            return None
    
    async def create_item(self, item_data: ItemCreate) -> dict:
        """สร้าง item ใหม่"""
        item_dict = item_data.model_dump()
        result = await self.collection.insert_one(item_dict)
        created_item = await self.collection.find_one({"_id": result.inserted_id})
        return self._format_item(created_item)
    
    async def update_item(self, item_id: str, item_data: ItemUpdate) -> Optional[dict]:
        """อัพเดท item"""
        try:
            update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
            if update_data:
                await self.collection.update_one(
                    {"_id": ObjectId(item_id)},
                    {"$set": update_data}
                )
            return await self.get_item_by_id(item_id)
        except:
            return None
    
    async def delete_item(self, item_id: str) -> bool:
        """ลบ item"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(item_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def _format_item(self, item: dict) -> dict:
        """แปลง MongoDB document เป็น dict"""
        if item:
            item["id"] = str(item.pop("_id"))
        return item
