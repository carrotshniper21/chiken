import subprocess
import requests
import json
import sys
import os
from utils import util
from pyfzf.pyfzf import FzfPrompt
from utils.arg_handler import parse_args

def choose_best_quality(qualities):
    ordered_qualities = ["1080", "720", "480", "360", "240", "auto"]

    for quality in ordered_qualities:
        if quality in qualities:
            return quality

    return qualities[0]

class MovieClient:
    def __init__(self):
        self.fzf = FzfPrompt()
        self.BASE_URL = "https://api.consumet.org/movies/flixhq/"

    def get_json_data(self, name):
        r = requests.get(f"{self.BASE_URL}{name}")
        return json.loads(r.text)

    def get_number_after_last_dash(self, s):
        parts = s.split("-")
        return int(parts[-1])

    def watch_movie(self, id, name):
        number = self.get_number_after_last_dash(id)
        p = requests.get(
            f"{self.BASE_URL}watch?episodeId={number}&mediaId={id}&server=vidcloud&"
        )
        return json.loads(p.text)

    def search_movies(self):
        try:
            print(util.colorcodes["Gray"] + "[*] This script is still in development so there will be some bugs!\nif you find any report them to: https://github.com/carrotshniper21/chiken" + util.colorcodes["Reset"])
            print(util.colorcodes["Yellow"] + "[*] INFO: " + util.colorcodes["Reset"] + "Fetching api.consumet.org\n")
            query = input("[+] Enter a show name: ")
            if query == "quit":
                sys.exit()
            json_data = self.get_json_data(query)
            if len(json_data["results"]) == 0:
                print(util.colorcodes["Red"] + "[X] ERROR: " + util.colorcodes["Reset"] + "No results found")
                sys.exit()

            strings = [
                f'{e["id"]}\t{e["title"]} ({e["type"]})' for e in json_data["results"]
            ]
            output = self.fzf.prompt(strings, "--border -1 --reverse --with-nth 2..")
            [id, name] = output[0].split("\t")
        except IndexError:
            sys.exit()

        return id, name

    def search_tv_shows(self, id, args):
        t = requests.get(f"{self.BASE_URL}info?id={id}")
        data = json.loads(t.text)
        episodes = data["episodes"]
        seasons = max(ep["season"] for ep in episodes)

        number_of_episodes = -1

        try:
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
        except ValueError:
            print(util.colorcodes["Red"] + "[X] ERROR: " + util.colorcodes["Reset"] + "Invalid Input. Try Again")
            sys.exit()

        episode_found = False

        for episode in episodes:
            if (
                episode["season"] == season_number
                and episode["number"] == episode_number
            ):
                episode_found = True
                break

        if not episode_found:
            print(util.colorcodes["Red"] + "[X] ERROR: " + util.colorcodes["Reset"] +  f"Episode {episode_number} not found.")
        else:
            h = requests.get(
                f"{self.BASE_URL}watch?episodeId={episode['id']}&mediaId={id}&server=vidcloud&"
            )
            show_episodes = json.loads(h.text)
            subtitles = [f'{z["url"]} {z["lang"]}' for z in show_episodes["subtitles"]]
            subtitle_data = [f'{z["url"]}' for z in show_episodes["subtitles"]]

            selected_episode = [
                f'{k["url"]} {k["quality"]}' for k in show_episodes["sources"]
            ]
            if args.sources:
                 print(util.colorcodes["Yellow"] + "[*] SOURCES " + util.colorcodes["Reset"] + f"{episode['title']}:\n" + util.colorcodes["Blue"] + "\n".join(selected_episode) + util.colorcodes["Reset"])
                 print(util.colorcodes["Yellow"] + "[*] SUBTITLES " + util.colorcodes["Reset"] + f"{episode['title']}:\n" + util.colorcodes["Blue"] + "\n".join(subtitles) + util.colorcodes["Reset"])
            sources = show_episodes["sources"]
            qualities = [source["quality"] for source in sources]
            best_quality = choose_best_quality(qualities)

            for subtitle_file in subtitle_data:
                subtitle_load = ' --sub-file=' + subtitle_file

            for source in sources:
                if source["quality"] == best_quality:
                    best_link = source["url"]
                    break

            if args.download:
                 download_arg = requests.get(best_link)
                 download_dir = input(util.colorcodes["Gray"] + "[*] Enter a directory to save to: " + util.colorcodes["Reset"])
                 if not os.path.exists(download_dir):
                     print(util.colorcodes["Red"] + "[X] ERROR: " + util.colorcodes["Reset"] + "Directory doesn't exist. Exiting.")

                 file_path = os.path.join(download_dir, "pp.m3u8")
                 with open(file_path, "w") as f:
                     f.write(download_arg.text)
                     print(util.colorcodes["Yellow"] + "[*] INFO: " + util.colorcodes["Reset"] + util.colorcodes["Bold"] + f"File Written: {episode['title']}" + util.colorcodes["Reset"])
                     sys.exit()
            print(["mpv", f"{best_link}", f"--title={episode['title']}", f"{subtitle_load}"])

            print(util.colorcodes["Green"] + "[*] SUCCESS: " + util.colorcodes["Reset"] + f"Now Playing '{episode['title']}'")
            print("[+] Press Ctrl+C to exit the program")
            tv_result = subprocess.run(
                ["mpv", f"{best_link}", f"--title={episode['title']}", f"{subtitle_load}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


def main():
    try:
        args = parse_args()
        movie_client = MovieClient()
        id, name = movie_client.search_movies()
        if id.startswith("tv/"):
            movie_client.search_tv_shows(id, args)
        elif id.startswith("movie/"):
            result = movie_client.watch_movie(id, name)
            media_link = [f'{p["url"]} {p["quality"]}' for p in result["sources"]]
            subtitles = [f'{z["url"]} {z["lang"]}' for z in result["subtitles"]]
            if args.sources:
                print(util.colorcodes["Yellow"] + "[*] SOURCES " + util.colorcodes["Reset"] + f"{name}:\n" + util.colorcodes["Blue"] + "\n".join(media_link) + util.colorcodes["Reset"])
                print(util.colorcodes["Yellow"] + "[*] SUBTITLES " + util.colorcodes["Reset"] + f"{name}:\n" + util.colorcodes["Blue"] + "\n".join(subtitles) + util.colorcodes["Reset"])
            qualities = [p["quality"] for p in result["sources"]]
            best_quality = choose_best_quality(qualities)

        for link in media_link:
            if best_quality in link:
                link = link.split()[0]
                print("[+] Press Ctrl+C to exit the program")
                result = subprocess.run(
                    ["mpv", "--fs", f"{link}", f"--title={name.rsplit(' ', 1)[0]}"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
    main()
