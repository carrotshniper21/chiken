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
            ]
            output = self.fzf.prompt(strings, "--border -1 --reverse --with-nth 2..")
            [id, name] = output[0].split("\t")
        except IndexError:
            sys.exit()

        return id, name

    def search_tv_shows(self, id):
        t = requests.get(f"{self.BASE_URL}/info?id={id}")
        data = json.loads(t.text)
        episodes = data["episodes"]
        seasons = max(ep["season"] for ep in episodes)

        number_of_episodes = -1

        if seasons > 1:
            season_number = int(input(f"[+] Please enter a season 1-{seasons}: "))
        else:
            season_number = 1

        for episode in episodes:
            if episode["season"] == season_number:
                number_of_episodes += 1

        episode_number = int(
            input(f"[+] Please enter an episode 1-{number_of_episodes}: ")
        )

        episode_found = False

        for episode in episodes:
            if (
                episode["season"] == season_number
                and episode["number"] == episode_number
            ):
                episode_found = True
                break

        if not episode_found:
            print(f"Episode {episode_number} not found.")
        else:
            h = requests.get(
                f"{self.BASE_URL}/watch?episodeId={episode['id']}&mediaId={id}&server=vidcloud&"
            )
            show_episodes = json.loads(h.text)
            selected_episode = [
                f'{k["url"]} {k["quality"]}' for k in show_episodes["sources"]
            ]
            sources = show_episodes["sources"]
            qualities = [source["quality"] for source in sources]
            best_quality = choose_best_quality(qualities)

            for source in sources:
                if source["quality"] == best_quality:
                    best_link = source["url"]
                    break

            print("[+] Press Ctrl+C to exit the program")
            tv_result = subprocess.run(
                ["mpv", f"{best_link}", f"--title={episode['title']}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


def main():
    try:
        movie_client = MovieClient()
        id, name = movie_client.search_movies()
        if id.startswith("tv/"):
            movie_client.search_tv_shows(id)
        elif id.startswith("movie/"):
            result = watch_movie(id, name)
            media_link = [f'{p["url"]} {p["quality"]}' for p in result["sources"]]
            subtitles = [f'{z["url"]} {z["lang"]}' for z in result["subtitles"]]
            qualities = [p["quality"] for p in result["sources"]]
            best_quality = choose_best_quality(qualities)

        for link in media_link:
            if best_quality in link:
                link = link.split()[0]
                print("[+] Press Ctrl+C to exit the program")
                result = subprocess.run(
                    ["mpv", f"{link}", f"--title={name.split()[0]}"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
    main()
