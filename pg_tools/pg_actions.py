import json
import os
import shutil
from mutagen.mp3 import MP3


def main():
    pass


# Save settings, playlist sections and list of working files
def save_state(working_list_of_files, settings):
    with open("settings.json", "w") as f:
        settings = json.dumps(settings)
        f.write(settings)
    with open("files.json", "w") as f:
        working_list_of_files = json.dumps(working_list_of_files)
        f.write(working_list_of_files)


# Load settings, playlist sections and list of working files
def load_state():
    missing_files = list()
    if os.path.isfile("settings.json"):
        with open("settings.json", "r") as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                settings = dict({"path": "./temp", "pl": [0, [], [], [], [], []]})
    else:
        settings = dict({"path": "./temp", "pl": [0, [], [], [], [], []]})
    path = settings["path"]
    if os.path.isfile("files.json"):
        with open("files.json", "r") as f:
            try:
                files = json.load(f)
            except json.JSONDecodeError:
                files = dict()
        for key in files:
            full_file_name = os.path.join(path, key)
            if not os.path.isfile(full_file_name):
                missing_files.append(key)
        for i in missing_files:
            files.pop(i)
    else:
        files = dict()
    if not files:
        files = dict()
    return settings, files, missing_files


# Set working path, copy all MP3 files from source folder to working folder and add files into GUI
def load_files_from_dir(src, destination="./temp/"):
    if not os.path.isdir(destination):
        os.mkdir(destination)
    new_files_list = dict()
    src_files = os.listdir(src)
    for file_name in src_files:
        full_file_name = os.path.join(src, file_name)
        if os.path.isfile(full_file_name) and file_name.lower().endswith('.mp3'):
            shutil.copy(full_file_name, destination)
            audio = MP3(full_file_name)
            file_length = audio.info.length
            # Two None values added to each file for future purposes (set priority, add comment etc.)
            new_files_list[file_name] = [int(file_length), None, None]
    if len(new_files_list) == 0:
        print("No mp3 files found")
    return new_files_list


# Copy single MP3 file from source folder to working folder and add files into GUI
def load_single_file(src, destination="./temp/"):
    if not os.path.isdir(destination):
        os.mkdir(destination)
    if src.lower().endswith('.mp3'):
        try:
            shutil.copy(src, destination)
        except shutil.SameFileError:
            return "File exists"
        file_name = os.path.basename(src)
        audio = MP3(src)
        file_length = audio.info.length
        new_files_list = {file_name: [int(file_length), None, None]}
        return new_files_list
    else:
        print("You can copy mp3 files only")


# Remove files from GUI panel and (by default) delete from working folder
def delete_files(working_list_of_files, files_to_delete, path=".", delete_file=True):
    for file in files_to_delete:
        if file in working_list_of_files.keys():
            working_list_of_files.pop(file)
        if delete_file:
            full_file_name = os.path.join(path, file)
            if os.path.isfile(full_file_name):
                os.remove(full_file_name)
    return working_list_of_files


# Calculate duration of all tracks in all playlist sections
def calculate_playlist_duration(working_list_of_files, pl):
    duration = 0
    for track in pl[1]:
        duration += working_list_of_files[track][0]
    for track in pl[2]:
        duration += working_list_of_files[track][0]
    for track in pl[3]:
        duration += working_list_of_files[track][0]
    for track in pl[4]:
        duration += working_list_of_files[track][0]
    for track in pl[5]:
        duration += working_list_of_files[track][0]
    return duration


# Remove track rom all playlist sections
def remove_from_pls(del_files, pl):
    for file in del_files:
        for i in range(len(pl[1])):
            if file in pl[1]:
                pl[1].remove(file)
        for i in range(len(pl[2])):
            if file in pl[2]:
                pl[2].remove(file)
        for i in range(len(pl[3])):
            if file in pl[3]:
                pl[3].remove(file)
        for i in range(len(pl[4])):
            if file in pl[4]:
                pl[4].remove(file)
        for i in range(len(pl[5])):
            if file in pl[5]:
                pl[5].remove(file)
    return pl


# Generate playlist.m3u file from all working playlist sections. Save to temp folder if no path received
def create_playlist(list_of_files, path="./temp"):
    # https://en.wikipedia.org/wiki/M3U
    if not os.path.isdir(path):
        os.mkdir(path)
    full_path = os.path.join(path, "playlist.m3u")
    with open(full_path, "w") as f:
        f.write('\n'.join(list_of_files))


if __name__ == '__main__':
    main()
