import jwt
import datetime

SECRET_KEY = "vetnurse-secret-key"
ALGORITHM = "HS256"

payload = {
    "sub": "1",
    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)
}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print(token)
