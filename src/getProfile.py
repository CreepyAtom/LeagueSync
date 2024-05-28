import json
import requests
from tabulate import tabulate

with open('./keys/riot_api.key', 'r') as file:
    api_key = file.read()


puuid_url = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/WPvIJ__t3lkaEX1mYt2OlNfbZ5h9znKGwcfO1_YSNk-yw_NV0YUa8HAAEZ8Htb7fL9jrbqPh2QgOzw"
username_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Borgomir/EUW"
last20matches_url = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/WPvIJ__t3lkaEX1mYt2OlNfbZ5h9znKGwcfO1_YSNk-yw_NV0YUa8HAAEZ8Htb7fL9jrbqPh2QgOzw/ids?start=0&count=20&api_key=RGAPI-b5128ee9-11b2-4e51-82d5-8077c573d30f"
match_url = "https://europe.api.riotgames.com/lol/match/v5/matches/EUW1_6951545470?api_key=RGAPI-b5128ee9-11b2-4e51-82d5-8077c573d30f"
def makeRequest(req):
    if ('?' in req):
        return requests.get(req + '&api_key=' + api_key)
    return requests.get(req + '?api_key=' + api_key)

def printResp(resp):
    print(resp.json())

def getUserPUUID(name,tag="EUW"):
    #Assuming the player is in EUW
    resp = makeRequest("https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/" + name + "/" + tag)
    return resp.json()['puuid']

def getName(puuid):
    resp = makeRequest("https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/" + puuid)
    return resp.json()['gameName']


def getLastMatches(name : str , tag : str = "EUW", nbGames : int = 20):
    puuid = getUserPUUID(name,tag)
    req = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids?start=0&count=" + str(nbGames)
    return makeRequest(req)

def getMatchData(matchId : str):
    req = "https://europe.api.riotgames.com/lol/match/v5/matches/" + matchId
    return makeRequest(req)

resp = getLastMatches("Borgomir")
printResp(resp)

def getMatchParticipantsFromID(matchId : str):
    resp = getMatchData(matchId).json()
    players = []
    for player in resp['info']['participants']:
        players.append([player['summonerName'], player['championName'], player['teamPosition']])
    return players

def getMatchParticipantsFromData(matchData : requests.models.Response):
    players = []
    for player in matchData.json()['info']['participants']:
        players.append([player['summonerName'], player['championName'], player['teamPosition']])
    return players

def load_match_types():
    with open('./common/matchTypes.json', 'r') as file:
        return json.load(file)
    
def get_match_type(queue_id, match_types):
    for match_type in match_types:
        if match_type['queueId'] == queue_id:
            return match_type['map']
    return None
    
def printMatchParticipants(matchId):
    players = getMatchParticipantsFromID(matchId)
    data = getMatchData(matchId).json()
    # Get match type
    queueId = data['info']['queueId']

    match_types = load_match_types()
    match_type = get_match_type(queueId, match_types)

    
    print("")
    # Separate players into blue and red sides
    blue_side = [player for player in players if player[2] in ['TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY']][:5]
    red_side = [player for player in players if player[2] in ['TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY']][5:]

    lanes = ['TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY']

    header = "League of Legends Match Participants".center(60, "=")
    header2 = f"{match_type}".center(60, "=")
    
    # ANSI escape codes for colors
    BLUE = '\033[94m'
    RED = '\033[91m'
    RESET = '\033[0m'
    
    blue_side_header = f"{BLUE}{'Blue Side'}{RESET}"
    red_side_header = f"{RED}{'Red Side'}{RESET}"

    table = []
    for lane in lanes:
        blue_player = next((player for player in blue_side if player[2] == lane), ["", "", ""])
        red_player = next((player for player in red_side if player[2] == lane), ["", "", ""])
        table.append([lane, f"{blue_player[0]} ({blue_player[1]})", f"{red_player[0]} ({red_player[1]})"])

    print(header)
    print(header2)
    print(tabulate(table, headers=[ "", blue_side_header, red_side_header], tablefmt="fancy_grid"))
    print("=" * 60)


for id in ['EUW1_6951545470', 'EUW1_6951460207', 'EUW1_6951377724', 'EUW1_6951316874', 'EUW1_6951243405', 'EUW1_6951194816']:
    printMatchParticipants(id)