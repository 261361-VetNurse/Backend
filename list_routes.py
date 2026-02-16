import sys
import os
from fastapi import FastAPI
from fastapi.routing import APIRoute

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.main import app
    print("Successfully imported app")
except ImportError as e:
    print(f"Error importing app: {e}")
    sys.exit(1)

print("\n=== Registered Routes ===")
for route in app.routes:
    if isinstance(route, APIRoute):
        print(f"{route.methods} {route.path}")
print("=========================\n")
