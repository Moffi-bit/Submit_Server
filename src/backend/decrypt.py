import base64
from dotenv import load_dotenv
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

load_dotenv()

DECRYPT_KEY = os.getenv("KEY")
IV = os.getenv("IV")

def decrypt(ciphertext):
        ciphertext = base64.b64decode(ciphertext)
        cipher = AES.new(DECRYPT_KEY.encode('utf-8'), AES.MODE_CBC, base64.b64decode(IV))

        return (unpad(cipher.decrypt(ciphertext), 16)).decode("utf-8", "ignore")
