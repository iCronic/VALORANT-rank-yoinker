



import time


class Pregame:
    def __init__(self, Requests, log):
        self.log = log

        self.Requests = Requests

        self.response = ""



    def get_pregame_match_id(self):
        global response
        try:
            response = self.Requests.fetch(url_type="glz", endpoint=f"/pregame/v1/players/{self.Requests.puuid}", method="get")
            if response.get("errorCode") == "RESOURCE_NOT_FOUND":
                return 0
            match_id = response['MatchID']
            self.log(f"retrieved pregame match id: '{match_id}'")
            return match_id
        except (KeyError, TypeError):
            self.log(f"cannot find pregame match id: {response}")
            # print(f"No match id found. {response}")
            try:
                self.response = self.Requests.fetch(url_type="glz", endpoint=f"/pregame/v1/players/{self.Requests.puuid}", method="get")
                match_id = self.response['MatchID']
                self.log(f"retrieved pregame match id: '{match_id}'")
                return match_id
            except (KeyError, TypeError):
                self.log(f"cannot find pregame match id: ")
                print(f"No match id found. {self.response}")
            return 0

    def get_pregame_stats(self):
        match_id = self.get_pregame_match_id()
        if match_id != 0:
            return self.Requests.fetch("glz", f"/pregame/v1/matches/{match_id}", "get")
        else:
            return None

    def instalock(self, match_id, agent_id):
        select_response = self.Requests.fetch(
            "glz",
            f"/pregame/v1/matches/{match_id}/select/{agent_id}",
            "post",
            max_retries=1,
        )
        if not isinstance(select_response, dict) or select_response.get("errorCode"):
            self.log(f"failed to select instalock agent: {select_response}")
            return False

        time.sleep(1)

        lock_response = self.Requests.fetch(
            "glz",
            f"/pregame/v1/matches/{match_id}/lock/{agent_id}",
            "post",
            max_retries=1,
        )
        if not isinstance(lock_response, dict) or lock_response.get("errorCode"):
            self.log(f"failed to lock instalock agent: {lock_response}")
            return False

        for team in lock_response.get("Teams", []):
            for player in team.get("Players", []):
                if player.get("Subject") == self.Requests.puuid:
                    return (
                        player.get("CharacterID", "").lower() == agent_id.lower()
                        and player.get("CharacterSelectionState") == "locked"
                    )
        return False
