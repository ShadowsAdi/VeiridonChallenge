import os
import threading
import time
from utils.proj_utils import ProjUtils
import json
import customtkinter as ctk
from tkinter import filedialog

base_directory = "clones"
results = {}

def process_subdirectories():
    subdirectories = [folder for folder in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, folder))]
    proj_utils = ProjUtils(plot.get())

    for subdir in subdirectories:
        start_time = time.time()
        full_path = os.path.join(base_directory, subdir)
        if not os.path.exists(full_path):
            continue
            
        clusters = proj_utils.group_documents(full_path)
        results[subdir] = clusters

        end_time = time.time()
        
        gui.after(0, update_gui, subdir, clusters, end_time - start_time)

    return results

def export_results_to_json(filename="exported_grouped_htmls.json"):
    if not results:
        text_output.insert("end", f"Results not processed yet")
        return

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    text_output.insert("end", f"\nResults exported to {filename}\n")

def update_gui(subdir, clusters, total_runtime):
    text_output.insert("end", f"Processed {subdir} folder and found {len(clusters)} groups of similar websites in {total_runtime:.2f} seconds:\n")
    for i, cluster in enumerate(sorted(clusters, key=len, reverse=True), 1):
        text_output.insert("end", f"\n   Group {i}: Contains {len(cluster)} similar websites -> {cluster}\n")
    text_output.insert("end", "\n")
    text_output.yview("end")

def browse_button():
    base_directory = filedialog.askdirectory()
    folder_path.set(base_directory)

def start_processing():
    base_directory = folder_path.get()
    
    if not base_directory or not os.path.isdir(base_directory):
        text_output.insert("end", "Error: Directory does not exist or it's invalid.\n")
    else:
        text_output.insert("end", f"\nProcessing dataset directory...\n")
        thread = threading.Thread(target=process_subdirectories, daemon=True)
        thread.start()

def main():
    ctk.set_appearance_mode("dark")

    global gui
    gui = ctk.CTk()  
    gui.title("HTML Clones")
    gui.geometry("580x600")
    gui.resizable(False, True)

    top_frame = ctk.CTkFrame(gui)
    top_frame.pack(pady=10, padx=10, fill="x")

    global folder_path
    folder_path = ctk.StringVar()

    ctk.CTkLabel(
        top_frame, 
        text="Base Directory:"
    ).grid(row=0, column=0, padx=5, pady=5)

    ctk.CTkEntry(
        top_frame, 
        textvariable=folder_path, 
        width=300
    ).grid(row=0, column=1, padx=5, pady=5)

    folder_path.set(base_directory)

    ctk.CTkButton(
        top_frame, 
        fg_color="#d9cf0d", 
        text_color="#000", 
        text="Browse", 
        command=browse_button
    ).grid(row=0, column=2, padx=5, pady=5)

    global plot
    plot = ctk.IntVar()

    ctk.CTkCheckBox(
        gui, 
        text="Plot clusters", 
        variable=plot
    ).pack(pady=5)

    ctk.CTkButton(
        gui, 
        fg_color="#d9cf0d", 
        text_color="#000", 
        text="Start Processing", 
        command=start_processing
    ).pack(pady=10)

    ctk.CTkButton(
        gui, 
        fg_color="#d9cf0d", 
        text_color="#000", 
        text="Export to JSON", 
        command=export_results_to_json
    ).pack(pady=10)

    global text_output
    text_output = ctk.CTkTextbox(
        gui, 
        width=580
    )
    text_output.pack(padx=10, pady=10, fill="both", expand=True)

    gui.mainloop()

if __name__ == '__main__':
    main()