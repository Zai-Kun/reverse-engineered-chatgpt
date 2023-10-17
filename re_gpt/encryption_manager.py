from cryptography.fernet import Fernet
import json
import base64
import os


class EncryptionManager:

    def __init__(self, secure_data_key=None, secure_data_path="data"):
        if secure_data_key:
            self.key = base64.b64encode(secure_data_key[:32].encode())
            self.cipher_suite = Fernet(self.key)
        else:
            self.key = None
        
        self.secure_data_path = secure_data_path

    def encrypt_and_save(self, json_data):
        data = json.dumps(json_data).encode()
        encrypted_data = self.cipher_suite.encrypt(data) if self.key else data

        with open(self.secure_data_path, 'wb') as file:
            file.write(encrypted_data)

    def read_and_decrypt(self):
        if os.path.exists(self.secure_data_path):
            with open(self.secure_data_path, 'rb') as file:
                encrypted_data = file.read()
                decrypted_data = self.cipher_suite.decrypt(encrypted_data) if self.key else encrypted_data
                return json.loads(decrypted_data.decode())
        else:
            return {}
