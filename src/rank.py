
class Rank:
    def __init__(self, Requests, log, content, ranks_before):
        self.Requests = Requests
        self.log = log
        self.ranks_before = ranks_before
        self.content = content
        self.requestMap = {}

    def get_request(self, puuid):
        if puuid in self.requestMap:
            return self.requestMap[puuid]

        response = self.Requests.fetch('pd', f"/mmr/v1/players/{puuid}", "get")
        self.requestMap[puuid] = response
        return response

    def invalidate_cached_responses(self):
        self.requestMap = {}

    #in future rewrite this code
    def get_rank(self, puuid, seasonID):
        response = self.get_request(puuid)
        final = {
            "rank": 0,
            "rr": 0,
            "leaderboard": 0,
            "peakrank": 0,
            "wr": "N/A",
            "numberofgames": 0,
            "peakrankact": None,
            "peakrankep": None,
            "statusgood": bool(getattr(response, "ok", False)),
            "statuscode": getattr(response, "status_code", None),
            }

        if not final["statusgood"]:
            self.log("failed getting rank")
            if response is not None:
                self.log(getattr(response, "text", str(response)))
            return final

        try:
            r = response.json()
            seasons = r["QueueSkills"]["competitive"].get(
                "SeasonalInfoBySeasonID", {}
            ) or {}
        except (TypeError, KeyError, ValueError):
            self.log("invalid rank response")
            return final

        if not isinstance(seasons, dict):
            self.log("invalid rank response")
            return final

        current_season = seasons.get(seasonID, {})
        if not isinstance(current_season, dict):
            current_season = {}
        try:
            rank_tier = int(current_season.get("CompetitiveTier", 0))
        except (TypeError, ValueError):
            rank_tier = 0
        if rank_tier >= 21:
            final["rank"] = rank_tier
            final["rr"] = current_season.get("RankedRating", 0)
            final["leaderboard"] = current_season.get("LeaderboardRank", 0)
        elif rank_tier not in (0, 1, 2):
            final["rank"] = rank_tier
            final["rr"] = current_season.get("RankedRating", 0)

        max_rank = final["rank"]
        max_rank_season = seasonID
        if seasons:
            for season, season_data in seasons.items():
                if not isinstance(season_data, dict):
                    continue
                if season_data.get("WinsByTier") is not None:
                    for winByTier in season_data["WinsByTier"]:
                        try:
                            win_tier = int(winByTier)
                        except (TypeError, ValueError):
                            continue
                        if season in self.ranks_before and win_tier > 20:
                            win_tier += 3
                        if win_tier > max_rank:
                            max_rank = win_tier
                            max_rank_season = season
        final["peakrank"] = max_rank

        try:
            wins = current_season["NumberOfWinsWithPlacements"]
            total_games = current_season["NumberOfGames"]
            final["numberofgames"] = total_games
            try:
                wr = int(wins / total_games * 100)
            except ZeroDivisionError: #no loses
                wr = 100
        except (KeyError, TypeError): #haven't played this season, #no data?
            # print("test")
            wr = "N/A"


        final["wr"] = wr

        #peak rank act and ep
        peak_rank_act_ep = self.content.get_act_episode_from_act_id(max_rank_season)
        final["peakrankact"] = peak_rank_act_ep["act"]
        final["peakrankep"] = peak_rank_act_ep["episode"]
        return final


if __name__ == "__main__":
    from constants import before_ascendant_seasons, version, NUMBERTORANKS
    from requestsV import Requests
    from logs import Logging
    from errors import Error
    import urllib3
    import pyperclip
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    Logging = Logging()
    log = Logging.log

    ErrorSRC = Error(log)

    Requests = Requests(version, log, ErrorSRC)
    #custom region
    # Requests.pd_url = "https://pd.na.a.pvp.net"

    #season id
    s_id = "67e373c7-48f7-b422-641b-079ace30b427" 

    r = Rank(Requests, log, before_ascendant_seasons)

    res = r.get_rank("", s_id)
    print(res)
    #[[rank, rr, leadeboard, peak rank, wr,] status]
    # print(f"Rank: {res[0][0]} - {NUMBERTORANKS[res[0][0]]}\nPeak Rank: {res[0][3]} - {NUMBERTORANKS[res[0][3]]}\nRR: {res[0][1]}\nLeaderboard: {res[0][2]}\nStatus is good: {res[1]}\nWR: {res[0][4]}%")
