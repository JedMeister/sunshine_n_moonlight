#!/usr/bin/python3

import requests
import subprocess
import json
import shutil
from os.path import join
from typing import Optional

URL = 'https://api.github.com/repos/LizardByte/Sunshine/releases'
CACHE = '/var/cache/apt/archives'

class SunshineInstallError(Exception):
    pass

class SunshineInstall:
    def __init__(self) -> None:
        self.latest_data = self._get_latest_data()

    @staticmethod
    def _get_latest_data() -> dict[str, str|int|bool|dict[str, str|int|bool]|list[dict]]:
        # get data from api
        r = requests.get(join(URL, 'latest'))
        return json.loads(r.content.decode('utf-8'))
		
    def _latest_url(self) -> str:
        assets = self.latest_data["assets"]
        assert isinstance(assets, list)
        for asset in assets:
            assert isinstance(asset, dict)
            if asset['name'] == 'sunshine-debian-bookworm-amd64.deb':
                return asset['browser_download_url']
        return ''

    @staticmethod
    def _download_file(url: str) -> str:
        local_filename = join(CACHE, url.split('/')[-1])
        with requests.get(url, stream=True) as r:
            with open(local_filename, 'wb') as fob:
                shutil.copyfileobj(r.raw, fob)
        return local_filename

    @staticmethod
    def _apt_install_deb(pkg: str) -> None:
        commands = (['apt-get', 'update'], ['apt-get', 'install', '-y', pkg])
        for command in commands:
            p = subprocess.run(command, capture_output=True, text=True)
            if p.returncode != 0:
                raise SunshineInstallError(f'apt error:\n{p.stderr}')

    @property
    def latest(self) -> str:
        tag_name = self.latest_data["tag_name"]
        assert isinstance(tag_name, str)
        return tag_name[1:]

    @property
    def installed(self) -> Optional[str]:
		# note this is not an fstring, it's a dpkg output formatting
        p = subprocess.run(['dpkg-query', '-W', '-f=${Version}', 'sunshine'],
					   	   capture_output=True, text=True)
        if p.returncode == 0:
            return p.stdout
        return None

    @property
    def update_available(self) -> bool:
        if not self.installed or self.latest > self.installed:
            return True
        return False

    def update(self) -> None:
        if self.update_available and self._latest_url():
                pkg = self._download_file(self._latest_url())
                self._apt_install_deb(pkg)
