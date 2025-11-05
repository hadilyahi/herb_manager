import hashlib
import os
import binascii

def hash_password(password: str) -> str:
    """تشفير كلمة المرور"""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwd_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                   salt, 100000)
    pwd_hash = binascii.hexlify(pwd_hash)
    return (salt + pwd_hash).decode('ascii')

def verify_password(stored_password: str, provided_password: str) -> bool:
    """التحقق من كلمة المرور"""
    salt = stored_password[:64]
    stored_pwd_hash = stored_password[64:]
    pwd_hash = hashlib.pbkdf2_hmac('sha512',
                                   provided_password.encode('utf-8'),
                                   salt.encode('ascii'),
                                   100000)
    pwd_hash = binascii.hexlify(pwd_hash).decode('ascii')
    return pwd_hash == stored_pwd_hash
