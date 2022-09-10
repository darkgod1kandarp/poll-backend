import base64 
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad

key = "fj8w4iw1cibhde6c"

def decrypt(enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        return unpad(cipher.decrypt(enc),16)