import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Use ttk for consistent button styling
import os
import requests
import subprocess  # For running another Python script
from process import filterm3u, makeobject, create_folders_and_strm_files_in_zip

# Local files to store the URL and fetched data
CONFIG_FILE = "url_config.txt"
DATA_FILE = "data_file.txt"

def load_url():
    """Load the stored URL from the local file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return file.read().strip()
    return ""

def save_url(url):
    """Save the URL to a local file."""
    with open(CONFIG_FILE, "w") as file:
        file.write(url)

def fetch_and_store_data(url):
    """Fetch content from the URL and store it to a local data file."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx

        with open("data.m3u", "wb") as file:
            file.write(response.content)

        success_label.config(text="Data retrieved and saved successfully!", fg="green")
        print("Data successfully fetched and saved to data.m3u.")

    except requests.exceptions.RequestException as e:
        success_label.config(text="Failed to fetch data. Check the URL.", fg="red")
        print(f"Failed to fetch data from the URL:\n{e}")

def run_filterm3u():
    """Run the `filterm3u` method."""
    try:
        filterm3u()
        messagebox.showinfo("Success", "M3U file has been filtered successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while filtering the M3U file:\n{e}")

def run_create_folders_and_strm():
    """Run the `create_folders_and_strm_files` method with data-filtered.m3u."""
    try:
        entries = makeobject("data-filtered.m3u")
        create_folders_and_strm_files_in_zip(entries)
        messagebox.showinfo("Success", "Folders and .strm files have been created!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while creating folders and .strm files:\n{e}")

def run_select_groups():
    """Run the `select-groups.py` script."""
    try:
        subprocess.run(["python", "select-groups.py"], check=True)
        messagebox.showinfo("Success", "Select Groups interface launched successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch select-groups.py:\n{e}")

def on_submit():
    """Handle the submission of the URL."""
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a valid URL.")
        return
    save_url(url)
    fetch_and_store_data(url)

# Create the main UI
root = tk.Tk()
root.title("m3u2files")
root.geometry("700x600")
root.configure(bg="#f5f5f5")  # Set a light background color

# Style configuration
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "TButton",
    background="#003366",
    foreground="white",
    font=("Arial", 10, "bold"),
    padding=5
)
style.map(
    "TButton",
    background=[("active", "#002244")],
    foreground=[("active", "white")]
)

# Header
header_frame = tk.Frame(root, bg="#003366", padx=10, pady=10)
header_frame.pack(fill="x")

welcome_label = tk.Label(
    header_frame,
    text="Welcome to m3u2files",
    font=("Arial", 20, "bold"),
    bg="#003366",
    fg="white"
)
welcome_label.pack()

# Content frame
content_frame = tk.Frame(root, bg="#f5f5f5", pady=20)
content_frame.pack(fill="both", expand=True)

# Description
explanation_label = tk.Label(
    content_frame,
    text=(
        "m3u2files is your go-to app for processing remote data into local STRM files.\n"
        "Simply enter a URL below, and we'll fetch, process, and structure it for you."
    ),
    wraplength=600,
    justify="center",
    bg="#f5f5f5",
    fg="#333333",
    font=("Arial", 12)
)
explanation_label.pack(pady=10)

# URL Entry
url_frame = tk.Frame(content_frame, bg="#f5f5f5")
url_frame.pack(pady=10)

url_label = tk.Label(url_frame, text="Enter the URL:", font=("Arial", 12), bg="#f5f5f5")
url_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

url_entry = tk.Entry(url_frame, width=50)
url_entry.grid(row=0, column=1, padx=5, pady=5)

previous_url = load_url()
if previous_url:
    url_entry.insert(0, previous_url)

url_entry.focus_set()

# Buttons frame
buttons_frame = tk.Frame(content_frame, bg="#f5f5f5", pady=20)
buttons_frame.pack()

# Define buttons with descriptions
button_descriptions = [
    ("Submit", "Fetch data from the URL and save locally.", on_submit),
    ("Open Select Groups", "Open the interface to select groups from the M3U file.", run_select_groups),
    ("Filter M3U File", "Filter the M3U file to include only selected groups.", run_filterm3u),
    ("Create Folders and STRM Files", "Create folders and STRM files in a zip archive.", run_create_folders_and_strm)
]

# Render buttons with descriptions
for i, (text, desc, command) in enumerate(button_descriptions):
    desc_label = tk.Label(buttons_frame, text=desc, font=("Arial", 10), bg="#f5f5f5", fg="#333333", anchor="w")
    desc_label.grid(row=i, column=0, sticky="w", padx=10, pady=5)
    button = ttk.Button(buttons_frame, text=text, command=command, width=30)
    button.grid(row=i, column=1, padx=10, pady=5)

# Success/Error label
success_label = tk.Label(content_frame, text="", font=("Arial", 10), bg="#f5f5f5", fg="#333333")
success_label.pack(pady=5)

# Footer
footer_frame = tk.Frame(root, bg="#003366", padx=10, pady=10)
footer_frame.pack(fill="x")

footer_label = tk.Label(
    footer_frame,
    text="© 2024 m3u2files - MIT License",
    font=("Arial", 10),
    bg="#003366",
    fg="white"
)
footer_label.pack()

# Start the application
root.mainloop()
