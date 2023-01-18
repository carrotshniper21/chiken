import subprocess
import argparse
import json
import sys
import os
from pyfzf.pyfzf import FzfPrompt
import requests

def parse_args():
    parser = argparse.ArgumentParser(
        description="Watch movies or anime from api.consumet.org"
    )

    parser.add_argument(
        "-q",
        "--quality",
        action="store",
        required=False,
        default="auto",
    )
    parser.add_argument(
        "-H",
        "--history",
        required=False,
        dest="history",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--download",
        required=False,
        dest="download",
        action="store_true",
    )
    parser.add_argument(
        "-u",
        "--update",
        required=False,
        dest="update",
        action="store_true",
    )
    parser.add_argument(
        "-C",
        "--continue",
        required=False,
        dest="continue",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--config",
        required=False,
        dest="config",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--vlc",
        required=False,
        dest="vlc",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--sources",
        required=False,
        dest="sources",
        action="store_true",
    )

    return parser.parse_args()

colorcodes = {
    "Black": "\033[30m",
    "Red": "\033[31m",
    "Green": "\033[32m",
    "Yellow": "\033[33m",
    "Blue": "\033[34m",
    "Magenta": "\033[35m",
    "Cyan": "\033[36m",
    "White": "\033[37m",
    "Reset": "\033[0m",
    "Bold": "\033[1m",
    "Gray": "\033[90m",
}

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

    def watch_movie(self, id, name, args):
        number = self.get_number_after_last_dash(id)
        if args.sources:
            print(colorcodes["Yellow"] + "[*] INFO " +  colorcodes["Reset"] + colorcodes["Bold"] + "Fetching Url:\n" + colorcodes["Reset"]  + colorcodes["Blue"] + f"{self.BASE_URL}watch?episodeId={number}&mediaId={id}&server=vidcloud&" + colorcodes["Reset"])
        p = requests.get(
            f"{self.BASE_URL}watch?episodeId={number}&mediaId={id}&server=vidcloud&"
        )
        return json.loads(p.text)

    def search_movies(self, args):
        try:
            print(colorcodes["Gray"] + "[*] This script is still in development so there will be some bugs!\nif you find any report them to: https://github.com/carrotshniper21/chiken" + colorcodes["Reset"])
            if args.sources:
                print(colorcodes["Yellow"] + "[*] INFO: " + colorcodes["Reset"] + colorcodes["Bold"] + "Fetching api.consumet.org" + colorcodes["Reset"])
            query = input("[+] Enter a show name: ")
            json_data = self.get_json_data(query)
            if len(json_data["results"]) == 0:
                print(colorcodes["Red"] + "[X] ERROR: " + colorcodes["Reset"] + "No results found")
                sys.exit()
            strings = [
                f'{e["id"]}\t{e["title"]} ({e["type"]})' for e in json_data["results"]
            ]
            if args.sources:
                print(colorcodes["Yellow"] + "[*] INFO: " + colorcodes["Reset"] + colorcodes["Bold"] + "Formatting Data:\n" + colorcodes["Reset"])
                print(colorcodes["Blue"] +  json.dumps(json_data, indent=4, separators=(". ", " = ")) + colorcodes["Reset"])
            output = self.fzf.prompt(strings, "--border -1 --reverse --with-nth 2..")
            [id, name] = output[0].split("\t")
        except IndexError as e:
            print(colorcodes["Red"] + "[X] ERROR: " + colorcodes["Reset"] + f"An error occured: {e}\n")
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
            print(colorcodes["Red"] + "[X] ERROR: " + colorcodes["Reset"] + "Invalid Input. Try Again")
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
            print(colorcodes["Red"] + "[X] ERROR: " + colorcodes["Reset"] +  f"Episode {episode_number} not found.")
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
                 print(colorcodes["Yellow"] + "[*] SOURCES " + colorcodes["Reset"] + colorcodes["Bold"] + f"{episode['title']}:\n" + colorcodes["Reset"] + colorcodes["Blue"] + "\n".join(selected_episode) + colorcodes["Reset"])
                 print(colorcodes["Yellow"] + "[*] SUBTITLES " + colorcodes["Reset"] + colorcodes["Bold"] +  f"{episode['title']}:\n" + colorcodes["Reset"] +  colorcodes["Blue"] + "\n".join(subtitles) + colorcodes["Reset"])
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
                 download_dir = input(colorcodes["Gray"] + "[*] Enter a directory to save to: " + colorcodes["Reset"])
                 if not os.path.exists(download_dir):
                     print(colorcodes["Red"] + "[X] ERROR: " + colorcodes["Reset"] + "Directory doesn't exist. Exiting.")

                 file_path = os.path.join(download_dir, "pp.m3u8")
                 with open(file_path, "w") as f:
                     f.write(download_arg.text)
                     print(colorcodes["Yellow"] + "[*] INFO: " + colorcodes["Reset"] + colorcodes["Bold"] + f"File Written: {episode['title']}" + colorcodes["Reset"])
                     sys.exit()
            print(colorcodes["Green"] + "[*] SUCCESS: " + colorcodes["Reset"] + f"Now Playing '{episode['title']}'")
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
        id, name = movie_client.search_movies(args)
        if id.startswith("tv/"):
            movie_client.search_tv_shows(id, args)
        elif id.startswith("movie/"):
            result = movie_client.watch_movie(id, name, args)
            media_link = [f'{p["url"]} {p["quality"]}' for p in result["sources"]]
            subtitles = [f'{z["url"]} {z["lang"]}' for z in result["subtitles"]]
            if args.sources:
                print(colorcodes["Yellow"] + "[*] SOURCES " + colorcodes["Reset"] + colorcodes["Bold"] + f"{name}:\n" + colorcodes["Reset"] + colorcodes["Blue"] + "\n".join(media_link) + colorcodes["Reset"])
                print(colorcodes["Yellow"] + "[*] SUBTITLES " + colorcodes["Reset"] + colorcodes["Bold"] + f"{name}:\n" + colorcodes["Reset"] + colorcodes["Blue"] + "\n".join(subtitles) + colorcodes["Reset"])
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
        sys.exit()


if __name__ == "__main__":
    main()
