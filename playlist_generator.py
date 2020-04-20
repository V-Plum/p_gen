"""
Modified PySimpleGUIQt_my module is added to this program package to support GetIndexes() method,
but default PySimpleGUIQt have to be installed as well to have all required additional libraries
To switch from PySimpleGUIQt to PySimpleGUI uncomment first line of code and comment second one in this file
and in pg_ui.py file
"""
# import PySimpleGUI  # Old Style GUI. More stable and functional, but ugly
from pg_tools import PySimpleGUIQt_my as sg  # Newer Qt-based GUI, mostly compatible with old one, but buggy
from pg_tools import pg_actions
from pg_tools import pg_ui
import random


def main():
    # Load saved settings, if available
    settings, files_list, missing_files = pg_actions.load_state()
    path = settings["path"]
    pl = settings["pl"]
    if not files_list:
        files_list = dict()

    # Removing deleted files from playlist sections, updating playlist duration
    if len(missing_files) > 0:
        sg.popup(f"{len(missing_files)} file(s) were removed from disk since last run")
        pl = pg_actions.remove_from_pls(missing_files, pl)
    pl_dur = pg_actions.calculate_playlist_duration(files_list, pl)

    # Calculate loaded files duration
    src_dur = 0
    for key in files_list:
        src_dur += files_list[key][0]
    file_names = sorted(list(files_list.keys()))

    # Window menu
    menu_def = [['&Help', ['&About']]]

    # Left panel layout
    all_files_layout = [
        [sg.Listbox(file_names, enable_events=False, key='-LIST-', size=(40, 22), select_mode="extended")],
        [sg.Text(f"Total files duration: {src_dur//60} min. {src_dur-(src_dur//60)*60} sec.",
                 key="td")]
    ]
    playlists_layout = list()

    # Right panel layouts. Only one have to be active depending on UI module:

    # 1. Use this layout for PySimpleGUIQt
    for i in range(1, 6):
        item = pg_ui.create_layout_item(i, pl[i])
        playlists_layout.append(item)
    playlists_layout.append([sg.Text(f"Playlist duration: {pl_dur//60} min. {pl_dur-(pl_dur//60)*60} sec.",
                                     key="pld")])

    # 2. Switch to this layout to work wit PySimpleGUI instead of PySimpleGUIQt
    # for i in range(1, 6):
    #     item = pg_ui.create_layout_item(i, pl[i], (40, 10))
    #     playlists_layout.append(item)
    # playlists_layout.append([sg.Text(f"Playlist duration: {pl_dur//60} min. {pl_dur-(pl_dur//60)*60} sec.",
    #                                  key="pld")])

    # Window layout assembly -- window menu, lift and right panels, bottom buttons
    layout = [
        [sg.Menu(menu_def, tearoff=False, pad=(200, 1))],
        [sg.Frame('All files', all_files_layout, font='Any 12', title_color='yellow', visible=True),
         sg.Frame('Create Playlist', playlists_layout, font='Any 12', title_color='yellow')],
        [sg.Button("Add Folder"), sg.Button("Add File"), sg.VerticalSeparator(pad=None), sg.Button("Delete Files"),
         sg.Button("Clear Playlist"), sg.VerticalSeparator(pad=None), sg.Button("Generate Playlist"), sg.Button("Exit")]
    ]
    window = sg.Window('Playlist Generator v0.2', layout)

    # Intercepting buttons events
    while True:
        event, values = window.read()
        if event is None or event == "Exit":
            exit()

        # Open About Window
        elif event == "About":
            pg_ui.about_window()

        # Add files from a source folder
        elif event == "Add Folder":
            src, path1 = pg_ui.open_folder_dialog(path)
            if src and path1:
                path = path1
                new_files_list = pg_actions.load_files_from_dir(src, path)
                files_list.update(new_files_list)
                file_names = sorted(list(files_list.keys()))
                src_dur = 0
                for key in files_list:
                    src_dur += files_list[key][0]
                window['-LIST-'].update(file_names)
                window['td'].update(f"Total files duration: {src_dur // 60} min. {src_dur - (src_dur // 60) * 60} sec.")

        # Add single file
        elif event == "Add File":
            src = pg_ui.open_file_dialog(path)
            if not src:
                sg.popup("Source path cannot be empty")
                continue
            new_file = pg_actions.load_single_file(src, path)
            if new_file == "File exists":
                sg.popup(f"File with the same name exists in destination folder {path}. Delete it and try again")
                continue
            files_list.update(new_file)
            file_names = sorted(list(files_list.keys()))
            src_dur = 0
            for key in files_list:
                src_dur += files_list[key][0]
            window['-LIST-'].update(file_names)
            window['td'].update(f"Total files duration: {src_dur // 60} min. {src_dur - (src_dur // 60) * 60} sec.")

        # Save all playlist sections to one playlist.m3u file
        elif event == "Generate Playlist":
            pg_actions.create_playlist(pl[1]+pl[2]+pl[3]+pl[4]+pl[5], path)
            sg.popup(f"{len(pl[1]+pl[2]+pl[3]+pl[4]+pl[5])} files added to playlist.m3u at {path}")

        # Remove items from playlist sections by index, update playlist duration:
        elif event in ("rm1", "rm2", "rm3", "rm4", "rm5"):
            pl_num = int(event[-1])
            pl_name = "pl" + str(event[-1])
            if values[pl_name]:
                track = values[pl_name][0]
                index = window[pl_name].GetIndexes()[0]
                pl[pl_num].pop(index)
                pl_dur -= files_list[track][0]
                window[pl_name].update(pl[pl_num])
                window['pld'].update(f"Playlist duration: {pl_dur//60} min. {pl_dur-(pl_dur//60)*60} sec.")

        # Add items to playlist sections, update playlist duration:
        elif event in ("add1", "add2", "add3", "add4", "add5"):
            if values['-LIST-']:
                pl_num = int(event[-1])
                pl_name = "pl" + str(event[-1])
                tracks = values['-LIST-']
                for track in tracks:
                    pl[pl_num].append(track)
                    pl_dur += files_list[track][0]
                window[pl_name].update(pl[pl_num])
                window['pld'].update(f"Playlist duration: {pl_dur // 60} min. {pl_dur - (pl_dur // 60) * 60} sec.")

        # Buttons UP and DOWN temporary doesn't work because of issue in .GetIndexes method in GUI framework
        # _Update: buttons UP and DOWN work with modified PySimpleGUIQt with .GetIndexes method added_

        # Move item UP in playlist section to sort manually. DOES NOT WORK WITH STANDARD PySimpleGUIQt
        elif event in ("up1", "up2", "up3", "up4", "up5"):
            pl_num = int(event[-1])
            pl_name = "pl" + str(event[-1])
            if values[pl_name]:
                index = window[pl_name].GetIndexes()[0]
                if index > 0:
                    pl[pl_num][index], pl[pl_num][index - 1] = pl[pl_num][index - 1], pl[pl_num][index]
                    window[pl_name].update(pl[pl_num])

        # Move item DOWN in playlist section to sort manually. DOES NOT WORK WITH STANDARD PySimpleGUIQt
        elif event in ("dn1", "dn2", "dn3", "dn4", "dn5"):
            pl_num = int(event[-1])
            pl_name = "pl" + str(event[-1])
            if values[pl_name]:
                index = window[pl_name].GetIndexes()[0]
                if index < len(pl[pl_num])-1:
                    pl[pl_num][index], pl[pl_num][index+1] = pl[pl_num][index+1], pl[pl_num][index]
                    window[pl_name].update(pl[pl_num])

        # Shuffle items in playlist sections:
        elif event in ("sh1", "sh2", "sh3", "sh4", "sh5"):
            pl_num = int(event[-1])
            pl_name = "pl" + str(event[-1])
            random.shuffle(pl[pl_num])
            window[pl_name].update(pl[pl_num])

        # Remove items from source section, optionally delete files:
        # 1. Popup if no files selected
        elif event == "Delete Files" and not values['-LIST-']:
            sg.popup("Select files in left panel first")

        # 2. Delete selected
        elif event == "Delete Files" and values['-LIST-']:
            tracks = values['-LIST-']
            decision = sg.popup_yes_no(f"Remove {len(tracks)} files from working list?")
            if decision == "Yes":
                pl = pg_actions.remove_from_pls(tracks, pl)
                window['pl1'].update(pl[1])
                window['pl2'].update(pl[2])
                window['pl3'].update(pl[3])
                window['pl4'].update(pl[4])
                window['pl5'].update(pl[5])
                pl_dur = pg_actions.calculate_playlist_duration(files_list, pl)
                window['pld'].update(f"Playlist duration: {pl_dur // 60} min. {pl_dur - (pl_dur // 60) * 60} sec.")
                decision = sg.popup_yes_no(f"Delete files from disk? This cannot be undone!")
                if decision == "Yes":
                    files_list = pg_actions.delete_files(files_list, tracks, path, delete_file=True)
                else:
                    files_list = pg_actions.delete_files(files_list, tracks, delete_file=False)
                src_dur = 0
                for key in files_list:
                    src_dur += files_list[key][0]
                file_names = sorted(list(files_list.keys()))
                window['-LIST-'].update(file_names)
                window['td'].update(f"Total files duration: {src_dur//60} min. {src_dur-(src_dur//60)*60} sec.")
            else:
                continue

        # Clear all playlist sections:
        elif event == "Clear Playlist":
            decision = sg.popup_yes_no("Are you sure you want to clear playlist?\nFiles will not be deleted")
            if decision == "Yes":
                pl = [0, [], [], [], [], []]
                settings = {"path": path, "pl": [0, [], [], [], [], []]}
                pg_actions.save_state(files_list, settings)
                window['pl1'].update(pl[1])
                window['pl2'].update(pl[2])
                window['pl3'].update(pl[3])
                window['pl4'].update(pl[4])
                window['pl5'].update(pl[5])
                pl_dur = pg_actions.calculate_playlist_duration(files_list, pl)
                window['pld'].update(f"Playlist duration: {pl_dur // 60} min. {pl_dur - (pl_dur // 60) * 60} sec.")
            else:
                continue

        # Save settings and list of files after each event
        settings = {"path": path, "pl": pl}
        pg_actions.save_state(files_list, settings)
    window.close()


if __name__ == '__main__':
    main()
