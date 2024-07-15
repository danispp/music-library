from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from tinydb import TinyDB, Query
import json


# Load your JSON data
with open('data.json', 'r') as f:
    music_data = json.load(f)

# Extract the list of artists from the 'artists' key
artists = music_data['artists']

# Initialize the database
db = TinyDB('data.json')
db.insert_multiple(artists)

# Query the database to display all artist names
User = Query()
results = db.search(User.name != '')


class MainScreen(Screen):
    def on_pre_enter(self, *args):
        self.load_artists()

    def load_artists(self):
        layout = self.ids.get('artists_layout')
        if layout is None:
            print("Error: 'artists_layout' not found")
            return
        layout.clear_widgets()

        with open('data.json', 'r') as f:
            self.music_data = json.load(f)
        self.artists = self.music_data['artists']

        for artist in self.artists:
            btn = MDRaisedButton(text=artist['name'], size_hint=(None, None), size=(200, 50),
                                     pos_hint={'x': 0, 'y':0})
            btn.bind(on_press=self.show_artist_details)
            layout.add_widget(btn)

    def show_artist_details(self, instance):
        artist_name = instance.text
        for artist in self.artists:
            if artist['name'] == artist_name:
                self.manager.current = 'artist_screen'
                self.manager.get_screen('artist_screen').display_artist(artist)
                break

    def on_search_text(self, instance, value):
        if not value:
            self.ids.suggestions_layout.clear_widgets()
            return

        self.suggestions = [artist['name'] for artist in self.artists if value.lower() in artist['name'].lower()]
        self.update_suggestions()

    def update_suggestions(self):
        suggestions_layout = self.ids.suggestions_layout
        suggestions_layout.clear_widgets()
        for suggestion in self.suggestions:
            suggestion_btn = MDRaisedButton(text=suggestion, size_hint=(None, None), size=(200, 50),
                                            pos_hint={'center_x': 0.5}, md_bg_color=[0, 1, 0, 1])
            suggestion_btn.bind(on_press=self.show_artist_details)
            suggestions_layout.add_widget(suggestion_btn)


class AlbumScreen(Screen):
    def display_album(self, album):
        layout = self.ids.get('album_info')
        if layout is None:
            print("Error: 'album_info' not found")
            return
        layout.clear_widgets()

        # Add album title
        album_title = MDLabel(
            text=f"Album: {album['title']}",
            size_hint_y=None,
            height=50,
            font_style="H5"
        )
        layout.add_widget(album_title)

        # Add album description
        album_description = MDLabel(
            text=album['description'],
            size_hint_y=None,
            height=100,
            font_style="Body1",
            theme_text_color="Secondary"
        )
        layout.add_widget(album_description)

        # Add a separator
        layout.add_widget(MDLabel(size_hint_y=None, height=20))

        # Add songs
        for song in album['songs']:
            song_label = MDLabel(
                text=f"  Song: {song['title']}; Length: {song['length']}",
                size_hint_y=None,
                height=30
            )
            layout.add_widget(song_label)


class ArtistScreen(Screen):
    def display_artist(self, artist):
        layout = self.ids.get('artist_info')
        if layout is None:
            print("Error: 'artist_info' not found")
            return
        layout.clear_widgets()

        label = MDLabel(text=f"Artist: {artist['name']}", size_hint_y=None, height=50, font_style="H5")
        layout.add_widget(label)
        for album in artist['albums']:
            album_button = MDRaisedButton(text=album['title'], size_hint=(None, None), size=(200, 50),
                                          pos_hint={'center_x': 0.5})
            album_button.bind(on_press=lambda x, a=album: self.show_album_details(a))
            layout.add_widget(album_button)

    def show_album_details(self, album):
        self.manager.current = 'album_screen'
        self.manager.get_screen('album_screen').display_album(album)


class MusicApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        Builder.load_file('myapp.kv')

        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main_menu'))
        sm.add_widget(ArtistScreen(name='artist_screen'))
        sm.add_widget(AlbumScreen(name='album_screen'))
        return sm

    def change_screen(self, screen_name):
        self.root.current = screen_name


if __name__ == '__main__':
    MusicApp().run()
