import streamlit as st
import os
from pathlib import Path

# --- Song Class ---
class Song:
    def __init__(self, title, artist):
        self.title = title
        self.artist = artist
        self.next_song = None

    def __str__(self):
        return f"{self.title} by {self.artist}"

# --- MusicPlaylist Class ---
class MusicPlaylist:
    def __init__(self):
        self.head = None
        self.current_song = None
        self.length = 0

    def add_song(self, title, artist):
        new_song = Song(title, artist)
        if self.head is None:
            self.head = new_song
            self.current_song = new_song
        else:
            current = self.head
            while current.next_song:
                current = current.next_song
            current.next_song = new_song
        self.length += 1
        st.success(f"Added: {new_song}")

    def display_playlist(self):
        if self.head is None:
            return []

        playlist_songs = []
        current = self.head
        count = 1
        while current:
            playlist_songs.append(f"{count}. {current.title} by {current.artist}")
            current = current.next_song
            count += 1
        return playlist_songs

    def play_current_song(self):
        if self.current_song:
            st.info(f"Now playing: {self.current_song}")
        else:
            st.warning("Playlist is empty or no song is selected to play.")

    def next_song(self):
        if self.current_song and self.current_song.next_song:
            self.current_song = self.current_song.next_song
        elif self.current_song and not self.current_song.next_song:
            st.warning("End of playlist. No next song.")
        else:
            st.warning("Playlist is empty.")

    def prev_song(self):
        if self.head is None or self.current_song is None:
            st.warning("Playlist is empty or no song is selected.")
            return
        if self.current_song == self.head:
            st.warning("Already at the beginning of the playlist.")
            return

        current = self.head
        while current.next_song != self.current_song:
            current = current.next_song
        self.current_song = current

    def get_length(self):
        return self.length

    def delete_song(self, title):
        if self.head is None:
            st.error(f"Cannot delete '{title}'. Playlist is empty.")
            return

        # If the song to be deleted is the head
        if self.head.title == title:
            if self.current_song == self.head:
                self.current_song = self.head.next_song
            self.head = self.head.next_song
            self.length -= 1
            st.success(f"Deleted: {title}")
            if self.length == 0:
                self.current_song = None
            return

        current = self.head
        prev = None
        while current and current.title != title:
            prev = current
            current = current.next_song

        if current:
            if self.current_song == current:
                if current.next_song:
                    self.current_song = current.next_song
                elif prev:
                    self.current_song = prev
                else:
                    self.current_song = None

            prev.next_song = current.next_song
            self.length -= 1
            st.success(f"Deleted: {title}")
        else:
            st.error(f"Song '{title}' not found in the playlist.")

# --- Streamlit App Layout ---
st.title("🎶 Music Playlist App")

# Initialize playlist in session state
if 'playlist' not in st.session_state:
    st.session_state.playlist = MusicPlaylist()

# Function to get available songs from song folder
def get_available_songs():
    song_dir = Path(__file__).parent / "song"
    if not song_dir.exists():
        return []
    
    # Get all audio files
    audio_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a'}
    songs = [f.stem for f in song_dir.iterdir() if f.suffix.lower() in audio_extensions]
    return sorted(songs)

# Sidebar for adding songs
st.sidebar.header("Add New Song")

# Tab for different input methods
tab1, tab2 = st.sidebar.tabs(["From File", "Manual Entry"])

with tab1:
    available_songs = get_available_songs()
    if available_songs:
        selected_song = st.selectbox("Select a song from your library", available_songs)
        if st.button("Add Song from Library"):
            # Extract title and artist from filename (format: Artist - Title.mp3)
            if " - " in selected_song:
                parts = selected_song.split(" - ", 1)
                artist = parts[0]
                title = parts[1]
            else:
                artist = "Unknown"
                title = selected_song
            st.session_state.playlist.add_song(title, artist)
    else:
        st.info("No songs found in the song folder")

with tab2:
    new_title = st.text_input("Title")
    new_artist = st.text_input("Artist")
    if st.button("Add Song to Playlist"):
        if new_title and new_artist:
            st.session_state.playlist.add_song(new_title, new_artist)
        else:
            st.warning("Please enter both title and artist.")

st.sidebar.markdown("--- 🎶")
st.sidebar.header("Delete Song")
delete_title = st.sidebar.text_input("Song Title to Delete")
if st.sidebar.button("Delete Song"):
    if delete_title:
        st.session_state.playlist.delete_song(delete_title)
    else:
        st.sidebar.warning("Please enter a song title to delete.")

# Main content for playlist display and controls
st.header("Your Current Playlist")
playlist_content = st.session_state.playlist.display_playlist()
if playlist_content:
    for song_str in playlist_content:
        st.write(song_str)
else:
    st.write("Playlist is empty. Add some songs from the sidebar!")

st.markdown("--- 🎶")
st.header("Playback Controls")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⏪ Previous"):
        st.session_state.playlist.prev_song()
        st.session_state.playlist.play_current_song()

with col2:
    if st.button("▶️ Play Current"):
        st.session_state.playlist.play_current_song()

with col3:
    if st.button("⏩ Next"):
        st.session_state.playlist.next_song()
        st.session_state.playlist.play_current_song()

st.markdown("--- 🎶")
st.write(f"Total songs in playlist: {st.session_state.playlist.get_length()} song(s)")