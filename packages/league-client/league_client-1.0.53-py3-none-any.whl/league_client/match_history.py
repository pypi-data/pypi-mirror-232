def get_match_history(connection, puuid):
    res = connection.get(f"/lol-match-history/v1/products/lol/{puuid}/matches")
    if not res.ok:
        return None
    return res.json()


def get_participants(connection, puuid, summoner_id):
    history = get_match_history(connection, puuid)
    if history is None:
        return []
    data = []
    for game in history["games"]["games"]:
        pid = None
        for p in game["participantIdentities"]:
            if p["player"]["summonerId"] == summoner_id:
                pid = p["participantId"]
                break
        if pid is None:
            continue
        for p in game["participants"]:
            if p["participantId"] == pid:
                data.append(p)
    return data


def get_flash_key(connection, puuid, summoner_id):
    participants = get_participants(connection, puuid, summoner_id)
    d_count = 0
    f_count = 0
    for p in participants:
        if p["spell1Id"] == 4:
            d_count += 1
        if p["spell2Id"] == 4:
            f_count += 1
    return "d" if d_count > f_count else "f"
