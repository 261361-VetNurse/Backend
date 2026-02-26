import base64
import json
import asyncio
import re
from google import genai
from app.config import settings

client = genai.Client(
    api_key=settings.GOOGLE_API_KEY
)


async def scan_medication_label(image_bytes: bytes, mime_type: str = "image/jpeg"):
    try:
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = """
        อ่านรูปภาพซองยาและสกัดข้อมูลในรูปแบบ JSON ภาษาไทยดังนี้:
        {
          "medicine_name": "",
          "dosage": "",
          "instruction": "",
          "frequency": "",
          "caution": ""
        }
        ถ้าไม่มีข้อมูลให้ใส่ ""
        ตอบกลับเฉพาะ JSON เท่านั้น
        """

        response = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-flash-latest',
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type, 
                                "data": image_base64,
                            }
                        }
                    ],
                }
            ],
        )

        text_content = response.text
        print("AI RAW:", text_content)

        match = re.search(r"\{.*\}", text_content, re.DOTALL)
        if not match:
            raise Exception("No JSON found in AI response")

        return json.loads(match.group())

    except Exception as e:
        raise Exception(f"OCR Processing Error: {str(e)}")