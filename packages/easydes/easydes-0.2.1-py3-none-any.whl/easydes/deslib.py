import base64
from Crypto.Cipher import DES
from Crypto.Util import Padding



def encrypt_des(plaintext: str, key: str):
    cipher = DES.new(key.encode("utf-8"), DES.MODE_ECB)
    padded_plaintext = Padding.pad(plaintext.encode("utf-8"), DES.block_size)
    encrypted = cipher.encrypt(padded_plaintext)
    return base64.b64encode(encrypted).decode("utf-8")


def decrypt_des(ciphertext: str, key: str):
    cipher = DES.new(key.encode("utf-8"), DES.MODE_ECB)
    padded_ciphertext = base64.b64decode(ciphertext.encode("utf-8"))
    decrypted = cipher.decrypt(padded_ciphertext)
    plaintext = Padding.unpad(decrypted, DES.block_size)
    return plaintext.decode("utf-8")
