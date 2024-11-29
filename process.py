# -*- coding: utf-8 -*-
"""
This script processes M3U files, filtering and extracting information based on user-selected groups.
It provides functions for filtering, extracting unique group titles, and parsing metadata.
"""

import re
import json
import os
import shutil  # Ensure this module is imported
import zipfile

# Configuration file storing the list of selected group titles
CONFIG_FILE = "selected_groups.json"

def load_selected_groups():
    """
    Load the selected groups from the JSON configuration file.

    :return: A list of selected group titles. Returns an empty list if the file does not exist.
    """
    if not os.path.exists(CONFIG_FILE):
        return []
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

def filterm3u():
    """
    Filter an M3U file to include only entries matching the selected group titles.
    The filtered content is written to 'data-filtered.m3u'.
    """
    # File paths
    input_file_path = 'data.m3u'
    output_file_path = 'data-filtered.m3u'

    # Load selected group titles
    selected_groups = set(load_selected_groups())

    # List to store filtered M3U lines
    filtered_lines = []

    # Read and process the input M3U file
    with open(input_file_path, 'r') as file:
        m3u_content = file.read()

    # Split the M3U content into lines
    lines = m3u_content.strip().split("\n")

    # Loop through lines to find matching group titles
    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            # Extract group-title metadata using regex
            group_title_match = re.search(r'group-title="([^"]+)"', lines[i])
            group_title = group_title_match.group(1) if group_title_match else None

            # Add lines to filtered list if the group title matches selected groups
            if group_title and group_title in selected_groups:
                filtered_lines.append(lines[i])  # Add metadata line
                if i + 1 < len(lines):          # Add corresponding URL line
                    filtered_lines.append(lines[i + 1])

    # Write the filtered lines to the output file
    with open(output_file_path, 'w') as output_file:
        output_file.write("\n".join(filtered_lines))

    print(f"Filtered data has been written to {output_file_path}.")

def makeobject(file_path):
    """
    Parse an M3U file and extract metadata and URLs into a list of dictionaries.

    :return: A list of dictionaries containing parsed metadata and URLs.
    """
    entries = []
    # file_path = 'data.m3u'

    # Read and process the M3U file
    with open(file_path, 'r') as file:
        m3u_content = file.read()

    # Split the M3U content into lines
    lines = m3u_content.strip().split("\n")

    # Loop through lines to extract metadata and URLs
    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            # Extract metadata using regex
            group_title_match = re.search(r'group-title="([^"]+)"', lines[i])
            group_title = group_title_match.group(1) if group_title_match else None

            tvg_id_match = re.search(r'tvg-id="([^"]*)"', lines[i])
            tvg_name_match = re.search(r'tvg-name="([^"]*)"', lines[i])
            tvg_logo_match = re.search(r'tvg-logo="([^"]*)"', lines[i])

            # Create a dictionary for the current entry
            entry = {
                "tvg_id": tvg_id_match.group(1) if tvg_id_match else None,
                "tvg_name": tvg_name_match.group(1) if tvg_name_match else None,
                "tvg_logo": tvg_logo_match.group(1) if tvg_logo_match else None,
                "group_title": group_title,
                "url": lines[i + 1] if i + 1 < len(lines) else None,
            }
            entries.append(entry)

    return entries

def get_unique_group_titles(entries):
    """
    Extract unique group-title values from a list of channel dictionaries.

    :param entries: List of dictionaries representing channels.
    :return: A set of unique group-title values.
    """
    return {entry['group_title'] for entry in entries if 'group_title' in entry}

def get_matching_objects(entries):
    """
    Retrieve objects from the given entries where the group_title matches the selected groups.

    :param entries: List of dictionaries containing channel metadata.
    :return: List of dictionaries matching the selected group titles.
    """
    selected_groups = set(load_selected_groups())
    return [entry for entry in entries if entry.get('group_title') in selected_groups]

def get_show_name(tvg_name):
    """
    Extract the show name from the tvg_name field by removing season/episode markers
    and " | 4K" suffix if present.

    :param tvg_name: The tvg_name string containing the show name, season/episode markers, and suffix.
    :return: The cleaned show name as a string.
    """
    # Remove " | 4K" if present
    tvg_name = tvg_name.replace(" | 4K", "")

    # Regex to find season and episode markers (e.g., S01 E02)
    pattern = r'(.*?)\sS\d{2}\sE\d{2}'
    match = re.match(pattern, tvg_name)

    if match:
        return match.group(1).strip()  # Return show name before markers
    return tvg_name.strip()            # Return cleaned name if no markers found

def list_unique_titles():
    """
    Extract and print a list of unique titles from the entries in 'data-filtered.m3u'.
    Titles are derived from the 'tvg_name' field using the `get_show_name` function.
    """
    input_file_path = 'data-filtered.m3u'

    # Set to store unique titles
    unique_titles = set()

    # Read and process the filtered M3U file
    try:
        with open(input_file_path, 'r') as file:
            m3u_content = file.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file_path}' not found.")
        return []

    # Split the M3U content into lines
    lines = m3u_content.strip().split("\n")

    # Loop through lines to extract titles
    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            # Extract tvg-name using regex
            tvg_name_match = re.search(r'tvg-name="([^"]*)"', lines[i])
            if not tvg_name_match:
                # print(f"No tvg-name found in line: {lines[i]}")
                continue

            tvg_name = tvg_name_match.group(1)
            # print(f"Found tvg_name: {tvg_name}")

            # Get the cleaned show name and add to the set
            show_name = get_show_name(tvg_name)
            unique_titles.add(show_name)

    # Print the list of unique titles to the console
    # print("Unique Titles:")
    # for title in sorted(unique_titles):
    #     print(title)

    return sorted(unique_titles)

def create_folders_for_unique_titles(unique_titles):
    """
    Create folders with each unique title as the folder name in the 'Library' directory.

    :param unique_titles: A list of unique titles to create folders for.
    """
    library_dir = 'Library'

    # Ensure the Library directory exists
    if not os.path.exists(library_dir):
        os.makedirs(library_dir)

    # Create a folder for each unique title
    for title in unique_titles:
        # Sanitize folder name to avoid issues with invalid characters
        sanitized_title = "".join(c for c in title if c.isalnum() or c in " _-").strip()
        folder_path = os.path.join(library_dir, sanitized_title)

        # Create the folder if it doesn't already exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    print(f"Created folders for {len(unique_titles)} unique titles in the '{library_dir}' directory.")

def clear_library_directory():
    """
    Clears all folders and their contents inside the 'Library' directory.
    """
    library_dir = 'VOD Files'

    # Check if the Library directory exists
    if not os.path.exists(library_dir):
        print(f"The '{library_dir}' directory does not exist. Nothing to clear.")
        return

    # Iterate over all items in the Library directory
    for item in os.listdir(library_dir):
        item_path = os.path.join(library_dir, item)

        # Remove directory or file
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)  # Delete the directory and its contents
        elif os.path.isfile(item_path):
            os.remove(item_path)  # Delete files if there are any

    print(f"Cleared all contents from the '{library_dir}' directory.")

def create_folders_and_strm_files(entries, library_path="VOD Files"):
    """
    Create folders based on the show name (from get_show_name) and place a .strm file
    within each folder. The .strm file's name is derived from the `tvg_name`.

    :param entries: List of dictionaries containing 'tvg_name' and 'url'.
    :param library_path: Path to the Library directory.
    """
    # Ensure the Library directory exists
    os.makedirs(library_path, exist_ok=True)

    for entry in entries:
        tvg_name = entry.get('tvg_name', '')
        url = entry.get('url', '')

        if not tvg_name or not url:
            print(f"Skipping entry due to missing tvg_name or url: {entry}")
            continue

        # Generate the show name using get_show_name
        show_name = get_show_name(tvg_name)

        # Create a folder for the show
        show_folder = os.path.join(library_path, show_name)
        os.makedirs(show_folder, exist_ok=True)

        # Create the .strm file inside the folder with the original tvg_name as the filename
        filename = os.path.join(show_folder, f"{tvg_name}.strm")

        try:
            # Write the URL to the .strm file
            with open(filename, "w") as strm_file:
                strm_file.write(url)

            # print(f"Created .strm file: {filename}")
        except Exception as e:
            print(f"Failed to create .strm file for {show_name}: {e}")

def write_files_to_nas(entries, nas_directory):
    """
    Write .strm files to a NAS directory using pysmb.

    :param entries: List of dictionaries containing 'tvg_name' and 'url'.
    :param nas_directory: The path to the folder on the NAS.
    """
    # Establish a connection
    conn = connect_to_nas()

    for entry in entries:
        tvg_name = entry.get('tvg_name', '')
        url = entry.get('url', '')

        if not tvg_name or not url:
            print(f"Skipping entry due to missing tvg_name or url: {entry}")
            continue

        # Get show name and prepare folder/file names
        show_name = get_show_name(tvg_name)
        folder_name = os.path.join(nas_directory, show_name)
        file_name = f"{tvg_name}.strm"

        try:
            # Ensure the directory exists
            conn.createDirectory(NAS_SHARE, folder_name)

            # Write the file content
            file_path = os.path.join(folder_name, file_name)
            with conn.openFile(NAS_SHARE, file_path, 'w') as file:
                file.write(url.encode('utf-8'))

            print(f"Created .strm file on NAS: {file_path}")
        except Exception as e:
            print(f"Failed to create .strm file for {show_name}: {e}")

    # Close the connection
    conn.close()

def create_folders_and_strm_files_in_zip(entries, zip_file_path="VOD.zip"):
    """
    Create a zip file containing folders (as logical structure) based on the show name (from get_show_name),
    and place a .strm file within each folder. The .strm file's name is derived from the `tvg_name`.

    :param entries: List of dictionaries containing 'tvg_name' and 'url'.
    :param zip_file_path: Path to the zip file to create or modify.
    """
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for entry in entries:
            tvg_name = entry.get('tvg_name', '')
            url = entry.get('url', '')

            if not tvg_name or not url:
                print(f"Skipping entry due to missing tvg_name or url: {entry}")
                continue

            # Generate the show name using get_show_name
            show_name = get_show_name(tvg_name)

            # Define the logical folder path inside the zip file
            show_folder = f"{show_name}/"

            # Define the file path within the zip
            file_name = f"{show_folder}{tvg_name}.strm"

            try:
                # Write the URL as the content of the .strm file in the zip
                zipf.writestr(file_name, url)
                print(f"Added .strm file to zip: {file_name}")
            except Exception as e:
                print(f"Failed to add .strm file for {show_name}: {e}")

    print(f"All files have been added to the zip file: {zip_file_path}")

# nas_library_path = "/volumeUSB1/usbshare/VOD Files"  # Folder on the NAS

# create_folders_and_strm_files(makeobject('data-filtered.m3u'))
# create_folders_and_strm_files_in_zip(makeobject('data-filtered.m3u'))

# write_files_to_nas(makeobject('data-filtered.m3u'), nas_library_path)

# clear_library_directory()

# print(makeobject('data-filtered.m3u'))
#
# for entry in makeobject('data-filtered.m3u'):
#     # print(entry)
#     print(get_show_name(entry['tvg_name']))
#     print(entry['tvg_name'])
#     print(entry['url'])


# print(list_unique_titles())
# create_folders_for_unique_titles(list_unique_titles())
# clear_library_directory()

# Uncomment this line to run the method
# list_unique_titles()

# Uncomment these lines to test the functions
# filterm3u()
# print(get_unique_group_titles(makeobject()))
# matching_objects = get_matching_objects(makeobject())
# for obj in matching_objects:
#     print(get_show_name(obj['tvg_name']))
