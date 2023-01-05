from lib.utils.colors import bad, warn
import subprocess
import requests
import signal
import json
import sys

def check_fzf():
    result = subprocess.run(["which", "fzf"], stdout=subprocess.PIPE)
    if result.stdout:
        pass
    else:
        user_choice = input("[!] This program needs fzf install? Y/N ")
        if user_choice.lower() == "y":
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "https://github.com/junegunn/fzf.git",
                    "~/.fzf",
                ]
            )
            subprocess.run(["~/.fzf/install"])
            subprocess.run(["clear"])
        if user_choice.lower() == "n":
            exit()

check_fzf()

from pyfzf.pyfzf import FzfPrompt

def install(packages):
    update_choice = input("[!] Update the needed packages? Y/N ")
    if update_choice.lower() == "y":
        subprocess.run(["pip", "install"] + packages)
    if update_choice.lower() == "n":
        subprocess.run(["clear"])

install(["requests", "BeautifulSoup4"])

def choose_best_quality(qualities):
    ordered_qualities = ["1080", "720", "480", "360", "240", "auto"]

    for quality in ordered_qualities:
        if quality in qualities:
            return quality

    return qualities[0]

def get_number_after_last_dash(s):
    parts = s.split("-")
    return int(parts[-1])

def watch_movie(id, name):
    number = get_number_after_last_dash(id)
    p = requests.get(
        f"https://api.consumet.org/movies/flixhq/watch?episodeId={number}&mediaId={id}&server=vidcloud&"
    )
    return json.loads(p.text)

class MovieClient:
    BASE_URL = "https://api.consumet.org/movies/flixhq"

    def __init__(self):
        self.fzf = FzfPrompt()

    def get_json_data(self, name):
        r = requests.get(f"{self.BASE_URL}/{name}")
        return json.loads(r.text)

    def search_movies(self):
        try:
            query = input("[+] Enter a show name: ")
            json_data = self.get_json_data(query)
            if len(json_data["results"]) == 0:
                print(f"{warn}No results found")
                sys.exit()

            strings = [
                f'{e["id"]}\t{e["title"]} ({e["type"]})' for e in json_data["results"]
from lib.utils.colors import bad, warn
import subprocess
import requests
import signal
import json
import sys

def check_fzf():
    result = subprocess.run(["which", "fzf"], stdout=subprocess.PIPE)
    if result.stdout:
        pass
    else:
        user_choice = input("[!] This program needs fzf install? Y/N ")
        if user_choice.lower() == "y":
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "https://github.com/junegunn/fzf.git",
                    "~/.fzf",
                ]
            )
            subprocess.run(["~/.fzf/install"])
            subprocess.run(["clear"])
        if user_choice.lower() == "n":
            exit()

check_fzf()

from pyfzf.pyfzf import FzfPrompt

def install(packages):
    update_choice = input("[!] Update the needed packages? Y/N ")
    if update_choice.lower() == "y":
        subprocess.run(["pip", "install"] + packages)
    if update_choice.lower() == "n":
        subprocess.run(["clear"])

install(["requests", "BeautifulSoup4"])

def choose_best_quality(qualities):
    ordered_qualities = ["1080", "720", "480", "360", "240", "auto"]

    for quality in ordered_qualities:
        if quality in qualities:
            return quality

    return qualities[0]

def get_number_after_last_dash(s):
    parts = s.split("-")
    return int(parts[-1])

def watch_movie(id, name):
    number = get_number_after_last_dash(id)
    p = requests.get(
        f"https://api.consumet.org/movies/flixhq/watch?episodeId={number}&mediaId={id}&server=vidcloud&"
    )
    return json.loads(p.text)

class MovieClient:
    BASE_URL = "https://api.consumet.org/movies/flixhq"

    def __init__(self):
        self.fzf = FzfPrompt()

    def get_json_data(self, name):
        r = requests.get(f"{self.BASE_URL}/{name}")
        return json.loads(r.text)

    def search_movies(self):
        try:
            query = input("[+] Enter a show name: ")
            json_data = self.get_json_data(query)
            if len(json_data["results"]) == 0:
                print(f"{warn}No results found")
                sys.exit()

            strings = [
                f'{e["id"]}\t{e["title"]} ({e["type"]})' for e in json_data["results"]
