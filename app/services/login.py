from app.config import settings
import urllib.parse

# ฟังก์ชันแสดงหน้าปุ่ม Login สีเขียว
def get_login_html():
    login_url = (
        f"https://access.line.me/oauth2/v2.1/authorize?"
        f"response_type=code&"
        f"client_id={settings.LOGIN_CLIENT_ID}&"  
        f"redirect_uri={settings.REDIRECT_URI}&" 
        f"state=vetnurse&"
        f"scope=profile%20openid"
    )
    
    return f"""
    <html>
        <head>
            <title>Vet Nurse Login</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #fff; }}
                .container {{ text-align: center; width: 90%; }}
                img {{ width: 100px; margin-bottom: 20px; }}
                .line-btn {{ background-color: #06C755; color: white; padding: 15px; border-radius: 10px; text-decoration: none; display: block; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <img src="https://cdn-icons-png.flaticon.com/512/2138/2138440.png">
                <h2>ยินดีต้อนรับสู่ Vet Nurse</h2>
                <p>กรุณาเข้าสู่ระบบด้วย LINE</p>
                <a class="line-btn" href="{login_url}">
                    เข้าสู่ระบบด้วย LINE
                </a>
            </div>
        </body>
    </html>
    """

# ฟังก์ชันแสดงหน้าประวัติการรักษา
def get_history_html(name: str, pic: str):
    return f"""
    <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial; padding: 20px; background-color: #f0f2f5; }}
                .profile {{ display: flex; align-items: center; margin-bottom: 20px; }}
                .profile img {{ width: 50px; height: 50px; border-radius: 50%; margin-right: 15px; border: 2px solid #00b900; }}
                .card {{ background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                h2 {{ color: #00b900; }}
            </style>
        </head>
        <body>
            <div class="profile">
                <img src="{pic}">
                <span>สวัสดีคุณ <b>{name}</b> ✨</span>
            </div>
            <div class="card">
                <h2>ประวัติการรักษา</h2>
                <p><b>ชื่อสัตว์เลี้ยง:</b> น้องส้มหยุด (แมว)</p>
                <hr>
                <p><b>20 ธ.ค. 2025:</b> ฉีดวัคซีนพิษสุนัขบ้า</p>
                <p><b>สถานะ:</b> ปกติ ✅</p>
            </div>
        </body>
    </html>
    """