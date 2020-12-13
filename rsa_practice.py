import rsa
import base64
from Crypto.Hash import SHA256,RIPEMD160
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Private key decryption
def fun1():

    (publicKey, privateKey) = rsa.newkeys(512)
    cipher = rsa.encrypt(b'Hello World!', publicKey)
    base64Text = base64.b64encode(cipher).decode()

    print(base64Text)

    text = rsa.decrypt(base64.b64decode(base64Text.encode()), privateKey)
    print(text.decode())

# Public key decryption
def fun2():

    publicKey, privateKey = rsa.newkeys(512)
    cipher = rsa.encrypt(b'Hello World!', publicKey)
    base64Text = base64.b64encode(cipher).decode()

    print(base64Text)

    text = rsa.decrypt(base64.b64decode(base64Text.encode()), privateKey) # AttributeError: 'PublicKey' object has no attribute 'blinded_decrypt'
    print(text.decode())

def fun3():
    return 'ass',400

if __name__ == '__main__':
    yuh = SHA256.new(data=b'Ass')
    yuhyuh = RIPEMD160.new(data=yuh.digest())
    print(type(yuh))
    print(len(yuh.digest()))
    print(yuh.digest())
    print(type(yuhyuh))
    print(len(yuhyuh.digest()))
    print(yuhyuh.digest())

    priv = RSA.generate(2048)
    pub = priv.publickey()

    message_in = b'Hello!'
    cipher = PKCS1_OAEP.new(pub)
    cipher_text = cipher.encrypt(message_in)

    print(cipher_text)

    cipher = PKCS1_OAEP.new(priv)
    message_out = cipher.decrypt(cipher_text)
    print(message_out)