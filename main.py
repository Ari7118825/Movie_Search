import tkinter as tk
from tkinter import ttk, messagebox
import requests

def search_movies():
    query = entry.get()
    if not query:
        return
    url = f"https://yts.mx/api/v2/list_movies.json?query_term={query}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        movies = data.get('data', {}).get('movies', [])
        if not movies:
            result_list.delete(0, tk.END)
            result_list.insert(tk.END, "No movies found.")
        else:
            result_list.delete(0, tk.END)
            for movie in movies:
                title = movie.get('title', 'Unknown Title')
                year = movie.get('year', 'Unknown Year')
                result_list.insert(tk.END, f"{title} ({year})")
    except requests.RequestException as e:
        result_list.delete(0, tk.END)
        result_list.insert(tk.END, f"An error occurred: {e}")

def show_movie_info():
    index = result_list.curselection()
    if index:
        selected_movie = result_list.get(index)
        url = f"https://yts.mx/api/v2/list_movies.json?query_term={selected_movie}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            movie_details = data.get('data', {}).get('movies', [])
            if movie_details:
                movie_info = movie_details[0]
                movie_title = movie_info.get('title', 'Unknown Title')
                movie_year = movie_info.get('year', 'Unknown Year')
                movie_description = movie_info.get('description_full', 'No description available.')
                # Open a new window to display movie info
                new_window = tk.Toplevel(root)
                new_window.title(f"Movie Info: {movie_title}")
                new_window.geometry("480x320")
                # Display movie info
                movie_info_label = tk.Label(new_window, text=f"Title: {movie_title}\nYear: {movie_year}\nDescription:")
                movie_info_label.pack(fill=tk.BOTH, expand=True)
                movie_description_text = tk.Text(new_window, wrap=tk.WORD, height=10)
                movie_description_text.insert(tk.END, movie_description)
                movie_description_text.pack(fill=tk.BOTH, expand=True)
                # Create a button to show torrent links
                show_torrent_button = ttk.Button(new_window, text="Show Torrent Links", command=lambda: show_torrents(movie_info))
                show_torrent_button.pack(pady=10)
        except requests.RequestException as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

def show_torrents(movie_info):
    movie_id = movie_info.get('id')
    url = f"https://yts.mx/api/v2/movie_details.json"
    categorized_torrents = {}
    try:
        response = requests.get(url, params={'movie_id': movie_id})
        response.raise_for_status()
        data = response.json()
        if 'data' in data and 'movie' in data['data'] and 'torrents' in data['data']['movie']:
            torrents = data['data']['movie']['torrents']
            for torrent in torrents:
                quality = torrent['quality']
                if "3D" not in quality:
                    if quality not in categorized_torrents:
                        categorized_torrents[quality] = []
                    categorized_torrents[quality].append(torrent['url'])
            # Open a new window to display torrent links
            new_window = tk.Toplevel(root)
            new_window.title(f"Torrent Links for {movie_info.get('title')}")
            new_window.geometry("200x300")
            # Create a text widget to display torrent links
            result_text = tk.Text(new_window, wrap=tk.WORD)
            result_text.pack(fill=tk.BOTH, expand=True)
            for quality, links in categorized_torrents.items():
                result_text.insert(tk.END, f"Quality: {quality}\n")
                for link in links:
                    result_text.insert(tk.END, f"Torrent: {link}\n")
                result_text.insert(tk.END, "-"*30 + "\n")  # Separate categories with a line
        else:
            messagebox.showinfo("Torrent Links", "No torrents found.")
    except requests.RequestException as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Create the main window
root = tk.Tk()
root.title("Movie Search")
root.geometry("480x240")

# Create a frame to contain the widgets
frame = ttk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Create the entry widget
entry = ttk.Entry(frame, width=40)
entry.grid(row=0, column=0, pady=10)

# Create the search button
search_button = ttk.Button(frame, text="Search", command=search_movies)
search_button.grid(row=0, column=1, pady=10)

# Create the result listbox widget
result_list = tk.Listbox(frame, width=50, height=10)
result_list.grid(row=1, column=0, columnspan=2, pady=10)

# Bind double-click event to show_movie_info function
result_list.bind("<Double-Button-1>", lambda event: show_movie_info())

root.mainloop()
