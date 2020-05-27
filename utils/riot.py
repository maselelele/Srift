from utils.config import SriftConfig
import requests as re
import json


class RiotConnection():
    def __init__(self):
        self.token = SriftConfig().getParsedConfig().get('riot', 'token')
        self.region = SriftConfig().getParsedConfig().get('riot', 'region').lower()

        # Check the API connection
        response = re.get(
            f'https://{self.region}.api.riotgames.com/lol/platform/v3/champion-rotations?api_key={self.token}')
        if response.status_code is not 200:
            print(f'Riot API request error: {response.status_code}')

    # Check if a summoner name is existing in specific region
    def verifySummonerName(self, summonerName, summonerRegion):
        response = re.get(
            f'https://{summonerRegion}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={self.token}')
        if response.status_code == 200:
            return True
        else:
            return False

    # Get the encryptedSummonerId from summonerName
    def getEncryptedSummonerIdByName(self, summonerName, summonerRegion):
        try:
            response = re.get(
                f'https://{summonerRegion}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={self.token}')
        except ConnectionError as conerr:
            print('Error connecting to api')
        data = json.loads(response.text)
        return data['id']

    # Check if the verification code is matching the summoner
    def verifySummonerCode(self, encryptedSummonerId, summonerRegion, summonerCode):
        response = re.get(
            f'https://{summonerRegion}.api.riotgames.com/lol/platform/v4/third-party-code/by-summoner/{encryptedSummonerId}?api_key={self.token}')

        if summonerCode == response.text.replace('"', ''):
            return True
        else:
            return False
