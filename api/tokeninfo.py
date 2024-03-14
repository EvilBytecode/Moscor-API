from flask import Flask, jsonify, request
import requests
from datetime import datetime

app = Flask(__name__)
# coded by evilbytecode aka codpulze aka sakura aka godfathercodepulze.
class MoscorTokenInfoAPI:
    def __init__(self, token):
        self.token = token
        self.headers = {'Authorization': f'{self.token}'}

    def tkninfo(self):
        req = requests.get("https://discord.com/api/v8/users/@me", headers=self.headers)
        if req.status_code == 200:
            data = req.json()
            username = data['username'] + "#" + data['discriminator']
            userID = data['id']
            phone = data.get('phone', 'Not provided')
            email = data.get('email', 'Not provided')
            language = data['locale']
            mfa = data['mfa_enabled']
            avatar_id = data['avatar']
            nitro = False
            res = requests.get('https://discordapp.com/api/v9/users/@me/billing/subscriptions', headers=self.headers)
            if res.status_code == 200:
                nitro_data = res.json()
                nitro = bool(len(nitro_data) > 0)
            avatar_url = f'https://cdn.discordapp.com/avatars/{userID}/{avatar_id}.webp'
            creation_date = datetime.utcfromtimestamp(((int(userID) >> 22) + 1420070400000) / 1000).strftime('%d-%m-%Y %H:%M:%S UTC')
            return {"username": username, "userID": userID, "phone": phone, "email": email, "language": language, "mfa_enabled": mfa, "avatar_url": avatar_url, "creation_date": creation_date, "nitro": nitro}
        else:
            # if it doesnt pass through then token invalid lol what do you expect..
            return jsonify({"error": "Invalid token or failed to retrieve data lol"}), 404

@app.route('/token_info', methods=['GET'])
def info():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Missing token"}), 400
    handler = MoscorTokenInfoAPI(token)
    info = handler.tkninfo()
    if info:
        return jsonify(info)
    else:
        return jsonify({"error": "Invalid token or failed to retrieve data"}), 404

if __name__ == '__main__':
    app.run(debug=True)
# modify last line based if its local or on replit lol its easy and someone who has 2 braincells knows.
