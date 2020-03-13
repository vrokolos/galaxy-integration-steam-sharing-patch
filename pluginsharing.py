import asyncio
import json
import logging
import platform
import random
import re
import os
import subprocess
import ssl
import sys
import webbrowser

from typing import Any, Dict, List, Optional
from galaxy.api.errors import AuthenticationRequired, UnknownBackendResponse
from galaxy.api.types import Achievement, Game, GameTime, LicenseInfo, GameLibrarySettings, UserPresence
from galaxy.api.plugin import create_and_run_plugin
from galaxy.api.consts import LicenseType
from plugin import logger, SteamPlugin, is_uri_handler_installed
from client import load_vdf, get_configuration_folder

class SteamSharingPlugin(SteamPlugin):
    def __init__(self, reader, writer, token):
        super().__init__(reader, writer, token)
        self._family_sharing_games: List[str] = []
        self._own_friends: List[FriendInfo] = []

    async def get_owned_games(self):
        owned_games = await super().get_owned_games()
        game_ids = list(map(lambda x: x.game_id, owned_games))
        other_games = await self.get_steam_sharing_games(game_ids)
        for i in other_games:
            owned_games.append(i)

        return owned_games

    async def get_steam_sharing_games(self, owngames: List[str]) -> List[Game]:
        profiles = list(
            filter(lambda x: "#" in x.user_name, self._own_friends))
        logger.info(profiles)
        newgames: List[Game] = []
        self._family_sharing_games = []
        for i in profiles:
            othergames = await self._client.get_games(i.user_id)

            try:
                for game in othergames:
                    hasit = any(f == str(game["appid"]) for f in owngames) or any(
                        f.game_id == str(game["appid"]) for f in newgames)
                    if not hasit:
                        self._family_sharing_games.append(str(game["appid"]))
                        newgame = Game(
                            str(game["appid"]),
                            game["name"],
                            [],
                            LicenseInfo(
                                LicenseType.OtherUserLicense, i.user_name)
                        )
                        newgames.append(newgame)
            except (KeyError, ValueError):
                logger.exception("Can not parse backend response")
                raise UnknownBackendResponse()
        return newgames

    async def _get_game_times_dict(self) -> Dict[str, GameTime]:
        game_times = await super()._get_game_times_dict()

        try:
            steamFolder = get_configuration_folder()
            vdfFile = os.path.join(
                steamFolder, "userdata", self._miniprofile_id, "config", "localconfig.vdf")
            logging.debug(f"Users Localconfig.vdf {vdfFile}")
            data = load_vdf(vdfFile)
            timedata = data["UserLocalConfigStore"]["Software"]["Valve"]["Steam"]["Apps"]
            for gameid in self._family_sharing_games:
                playTime = 0
                lastPlayed = 86400
                if gameid in timedata:
                    item = timedata[gameid]
                    if 'playtime' in item:
                        playTime = item["playTime"]
                    if 'lastplayed' in item:
                        lastPlayed = item["LastPlayed"]
                game_times[gameid] = GameTime(gameid, playTime, lastPlayed)
        except (KeyError, ValueError):
            logger.exception("Can not parse friend games")

        return game_times

    async def get_friends(self):
        self._own_friends = await super().get_friends()
        return self._own_friends

    async def launch_game(self, game_id):
        await super().launch_game(game_id)

    async def install_game(self, game_id):
        await super().install_game(game_id)

    async def uninstall_game(self, game_id):
        await super().uninstall_game(game_id)

    async def shutdown_platform_client(self) -> None:
        return await super().shutdown_platform_client()

    async def get_user_presence(self, user_id: str, context: Any) -> UserPresence:
        return await super().get_user_presence(user_id, context)
        
    async def get_local_games(self):
        return await super().get_local_games()


def main():
    create_and_run_plugin(SteamSharingPlugin, sys.argv)


if __name__ == "__main__":
    main()
