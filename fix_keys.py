from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_keys():
    # 1. สร้าง Private Key (RSA 2048-bit)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 2. บันทึก Private Key เป็นรูปแบบ PKCS#8 
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open("private.key", "wb") as f:
        f.write(private_pem)

    # 3. บันทึก Public Key เป็นรูปแบบ SubjectPublicKeyInfo
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open("public.key", "wb") as f:
        f.write(public_pem)

    print(" สร้างไฟล์ private.key และ public.key สำเร็จแล้ว")
    print("\n--- เนื้อหาใน public.key ---")
    print(public_pem.decode())
    print("--------------------------------------------------")

if __name__ == "__main__":
    generate_keys()