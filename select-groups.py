import tkinter as tk
from tkinter import messagebox
import json
import os
import process

# File to store the selected groups
CONFIG_FILE = "selected_groups.json"

def load_config():
    """Load the stored group selections from a file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return []

def save_config(selected_groups):
    """Save the selected groups to a file."""
    with open(CONFIG_FILE, "w") as file:
        json.dump(selected_groups, file)

def on_save():
    """Handle saving the selected groups."""
    selected_groups = [group for group, var in check_vars.items() if var.get()]
    save_config(selected_groups)
    messagebox.showinfo("Success", "Selected groups have been saved!")

def create_ui(unique_groups):
    """Create the UI for selecting groups."""
    root = tk.Tk()
    root.title("Group Selector")
    root.geometry("700x600")
    root.configure(bg="#f5f5f5")  # Light background for consistency

    # Header
    header_frame = tk.Frame(root, bg="#003366", padx=10, pady=10)
    header_frame.pack(fill="x")

    header_label = tk.Label(
        header_frame,
        text="Group Selector",
        font=("Arial", 20, "bold"),
        bg="#003366",
        fg="white"
    )
    header_label.pack()

    # Explanation Text
    explanation_label = tk.Label(
        root,
        text="Select the groups you want to track and save your preferences.",
        font=("Arial", 12),
        bg="#f5f5f5",
        fg="#333333",
        wraplength=650,
        justify="center",
        pady=10
    )
    explanation_label.pack()

    # Frame for Canvas and Scrollbar
    frame = tk.Frame(root, bg="#f5f5f5", pady=10)
    frame.pack(fill="both", expand=True, padx=10)

    # Canvas for Scrollable Content
    canvas = tk.Canvas(frame, bg="#f5f5f5", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview, bg="#f5f5f5")
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Frame Inside Canvas
    checkbox_frame = tk.Frame(canvas, bg="#f5f5f5")
    canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")

    # Create Checkboxes for Each Group
    for group in unique_groups:
        var = tk.BooleanVar(value=group in initial_selected_groups)
        check_vars[group] = var
        checkbox = tk.Checkbutton(
            checkbox_frame,
            text=group,
            variable=var,
            font=("Arial", 10),
            bg="#f5f5f5",
            fg="#333333",
            anchor="w",
            padx=5
        )
        checkbox.pack(fill="x", padx=10, pady=2)

    # Update Scroll Region
    def update_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    checkbox_frame.bind("<Configure>", update_scroll_region)

    # Save Button
    save_button = tk.Button(
        root,
        text="Save",
        command=on_save,
        width=20,
        bg="#003366",
        fg="white",
        font=("Arial", 12, "bold"),
        activebackground="#002244",
        activeforeground="white",
        pady=5
    )
    save_button.pack(pady=10)

    # Footer
    footer_frame = tk.Frame(root, bg="#003366", padx=10, pady=10)
    footer_frame.pack(fill="x")

    footer_label = tk.Label(
        footer_frame,
        text="© 2024 Group Selector - All rights reserved",
        font=("Arial", 10),
        bg="#003366",
        fg="white"
    )
    footer_label.pack()

    root.mainloop()


# Generate Data and Launch the UI
result = process.makeobject('data.m3u')
result = process.get_unique_group_titles(result)
result = sorted(title.strip() for title in result)

entries = [{'group_title': title} for title in result]

# Load the initially selected groups
initial_selected_groups = load_config()

# Dictionary to hold the checkbutton variables
check_vars = {}

# Launch the UI
create_ui(result)
