import base64, json
from Crypto.Hash import SHA256

from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from models.config import Config
from services.stager import Stager
from services.time import Time


class CryptoManager(object):
    def __init__(self, Session):
        super().__init__()
        self.Session = Session
        self.private_key = None
        self.public_key = None
        self.keyPrefix = ""

    def setKeyPrefix(self, prefix: str):
        self.keyPrefix = prefix

    def set_password(self, password, is_remote_write):
        if not self.is_loaded():
            return
        if password == "" or password == None:
            password = 'TestPassword'
        e_key_pem = self.encrypt_with_password(password.encode(), self.private_key.export_key())
        self.save_keys(self.private_key, e_key_pem.decode())
        stager = Stager(self.Session(), is_remote_write)
        stager.stage_config(self)
        stager.commit()

    def load_keys(self, password = None):
        check = self.password_and_key_check(password)
        if check['pass_state'] == 'correct' or check['pass_state'] == 'default':
            self.private_key = check['key']
            self.public_key = self.private_key.public_key()
            self.save_keys(self.private_key)
        return check['pass_state']

    def save_keys(self, pr_key, e_pr_pem = None, pu_pem = None):
        session = self.Session()
        if pu_pem == None and type(pr_key) != type(None):
            pu_key = pr_key.publickey()
            pu_pem = pu_key.export_key().decode()
        pu_pem = Config(
            config = self.keyPrefix + "public_key_pem",
            value = pu_pem,
            annotation = "key",
            status = "UP",
            _timestamp_ = Time().get_time_in_micro(),
            _signature_ =  ""
        )
        if e_pr_pem != None:
            e_pr_pem = Config(
                config = self.keyPrefix + "e_private_key_pem",
                value = e_pr_pem,
                annotation = "key",
                status = "UP",
                _timestamp_ = Time().get_time_in_micro(),
                _signature_ =  ""
            )
        if pu_pem != None:
            session.merge(pu_pem)
        if e_pr_pem != None:
            session.merge(e_pr_pem)
        session.commit()
        session.close()

    def get_encrypted_key(self):
        session = self.Session()
        key = session.query(Config).filter(Config.config == self.keyPrefix + "e_private_key_pem").first()
        if key != None:
            key = key.value
        session.close()
        return key

    def get_public_key(self):
        session = self.Session()
        key = session.query(Config).filter(Config.config == self.keyPrefix + "public_key_pem").first()
        if key != None:
            key = key.value
            self.public_key = RSA.import_key(key)
        session.close()
        return key

    def password_and_key_check(self, password, reinit = False):
        e_key_pem = self.get_encrypted_key() if not reinit else None
        if e_key_pem != None:
            e_key_pem = e_key_pem.encode()
        default = b'TestPassword'
        if e_key_pem == None:
            key = self.new_private_key()
            e_key_pem = self.encrypt_with_password(default, key.export_key())
            self.save_keys(key, e_key_pem.decode())

        try:
            pr_key = self.decrypt_with_password(default, e_key_pem)
            # load key
            private_key = RSA.import_key(pr_key)
            if password != None and password != '':
                return { 'key': private_key, 'pass_state': 'overload' }
            return { 'key': private_key, 'pass_state': 'default' }
        except ValueError:
            return self.password_and_key_check(password, reinit = True)
        except InvalidToken:
            if password == None or password == '':
                return { 'key': None, 'pass_state': 'none' }
            try:
                pr_key = self.decrypt_with_password(password.encode(), e_key_pem)
                # load key
                private_key = RSA.import_key(pr_key)
                return { 'key': private_key, 'pass_state': 'correct' }
            except ValueError:
                return self.password_and_key_check(None, reinit = True)
            except InvalidToken:
                return { 'key': None, 'pass_state': 'wrong' }

    def get_password_token(self, password):
        salt = b'P\xf3\xf8+T\xbf\x8d\x8f\xf2*\x0eE\xc4X\xbb\xd3'
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def encrypt_with_password(self, passwd, source):
        fernet = Fernet(self.get_password_token(passwd))
        encrypted = fernet.encrypt(source)
        return encrypted

    def decrypt_with_password(self, passwd, source):
        fernet = Fernet(self.get_password_token(passwd))
        decrypted = fernet.decrypt(source)
        return decrypted

    def encrypt_with_key(self, source: str) -> str:
        self.get_public_key()
        if not self.is_pub_loaded():
            return
        cipher = PKCS1_OAEP.new(key=self.public_key)
        result = ""
        while True:
            part = source[0:86]
            source = source[86:]
            result += cipher.encrypt(part.encode()).hex()
            if len(source) == 0:
                break
            else: result += '-'
        return result

    def is_loaded(self):
        return type(self.private_key) != type(None) and type(self.public_key) != type(None)

    def is_pub_loaded(self):
        return type(self.public_key) != type(None)

    def decrypt_with_key(self, source: str) -> str:
        if not self.is_loaded():
            return
        cipher = PKCS1_OAEP.new(key=self.private_key)
        result = ""
        for part in source.split('-'):
            part = bytes.fromhex(part)
            result += cipher.decrypt(part).decode()
        return result

    def new_private_key(self):
        private_key = RSA.generate(1024)
        return private_key        
    
    def sign(self, payload):
        if not self.is_loaded():
            return
        if type(payload) != str:
            payload = self.serialize_object(payload)
        signer = PKCS1_v1_5.new(self.private_key)
        digest = SHA256.new(payload.encode())
        sig = signer.sign(digest)
        return sig.hex()

    def verify_signature(self, payload, signature):
        self.get_public_key()
        verified = False
        if not self.is_pub_loaded():
            # NO PUBLIC KEY ERROR
            return verified
        try:
            if type(payload) != str:
                payload = self.serialize_object(payload)
            verifier = PKCS1_v1_5.new(self.public_key)
            digest = SHA256.new(payload.encode())
            verified = verifier.verify(digest, bytes.fromhex(signature))
        except: pass
        return verified

    def serialize_object(self, obj):
        encoder = json.JSONEncoder(skipkeys=True, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys= True, default=lambda o: '<non-serializable>')
        value = encoder.encode(obj)
        if value == '"<non-serializable>"':
            attributes = { attr: obj.__getattribute__(attr) for attr in dir(obj) if not callable(obj.__getattribute__(attr)) and self.is_serializable(obj.__getattribute__(attr)) and not attr.startswith('_') }
            value = encoder.encode(attributes)
        return value

    def is_serializable(self, value):
        try: json.JSONEncoder().encode(value)
        except: return False
        return True


