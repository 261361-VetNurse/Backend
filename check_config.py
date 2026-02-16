import sys
import os

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.config import settings
    print(f"R2_ACCESS_KEY_ID: '{settings.R2_ACCESS_KEY_ID}'")
    print(f"R2_SECRET_ACCESS_KEY: '{settings.R2_SECRET_ACCESS_KEY}'")
    print(f"R2_PUBLIC_URL: '{settings.R2_PUBLIC_URL}'")
    
    if not settings.R2_ACCESS_KEY_ID:
        print("❌ R2_ACCESS_KEY_ID is empty")
    else:
        print("✅ R2_ACCESS_KEY_ID is set")
        
except ImportError as e:
    print(f"Error importing app: {e}")
except Exception as e:
    print(f"Error: {e}")
