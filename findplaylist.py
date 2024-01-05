import requests
import os
from dotenv import load_dotenv
import base64
import json

# We will try to get one playlists from the user first

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_auth_header_cc():
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    header = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type" : "application/x-www-form-urlencoded"
    }
        
    form = {
        "grant_type": "client_credentials"
    }
    
    # We will be sending a Post request 
        
    result = requests.post(url=url, headers=header, data=form)
    json_result =  json.loads(result.content)
    
    token = json_result["access_token"]
    
    return {
        "Authorization" : "Bearer " + token
    }
    
class Song:
    def __init__(self, query_word):
        self.query = query_word
        self.track_item = self.get_song_from_search_json()
        self.track_name = self.track_item["name"]
        self.track_album = self.track_item["album"]["name"]
        
    def get_name(self):
        return self.track_name
    
    def get_id(self):
        return self.track_item["id"]        
        
    def get_song_from_search_json(self):
        url = "https://api.spotify.com/v1/search"
        headers = get_auth_header_cc()
        
        updated_song = ""
        for char in self.query:
            if char == " ":
                updated_song += "+"
            else:
                updated_song += char

                    
        query = f"?q={updated_song}&type=track&market=US&limit=1&offset=0"
        
        query_url = url + query
            
        result = requests.get(url=query_url, headers=headers)
        
        json_result = json.loads(result.content)
        
        track_item_json = json_result["tracks"]["items"][0]
        
        return track_item_json
    
    def get_artists(self):
        artists = []
        for index, value in enumerate(self.track_item["artists"]):
            for k, c in self.track_item["artists"][index].items():
                if k == "name":
                    artists.append(c)
                    continue
                
        if len(artists) == 1:
            return artists[0]
        else:
            return artists
            
            
    
    
    

# Let's get a song from a search query
class Playlist:
    def __init__(self, playlist_id, market="US"):
        self.playlist_id = playlist_id
        self.market = market
        self.playlist_json = self.get_json_playlist()
        self.playlist_name = self.playlist_json["name"]
        self.playlist_owner = self.playlist_json["owner"]["display_name"]
        self.playlist_url = self.playlist_json["owner"]["external_urls"]["spotify"]
        
    def get_json_playlist(self):
        url = f"https://api.spotify.com/v1/playlists/{self.playlist_id}"
        headers = get_auth_header_cc()
        
        query = f"?market={self.market}"
                
        query_url = url + query
        
        result = requests.get(url=query_url, headers=headers)

        json_result = json.loads(result.content)
        
        return json_result
    
    def get_playlist_name(self):
        return self.playlist_name
    
    def get_playlist_ownder(self):
        return self.playlist_name
    
    def get_playlist_url(self):
        return self.playlist_url
    
    def get_songs_array(self):
        
        tmp = []
        
        print(type(self.playlist_json["tracks"]["items"]))
                    
        for index, track_dict in enumerate(self.playlist_json["tracks"]["items"]):
            for k, c in self.playlist_json["tracks"]["items"][index].items():
                if k == "track":
                    for i, j in self.playlist_json["tracks"]["items"][index][k].items():
                        if i == "name":
                            tmp.append(j)
                            continue
                    
        return tmp
    
    def print_songs(self):
        
        song_list = self.get_songs_array()
        for index, song in enumerate(song_list):
            print(f"\n {index+1}. {song}")
                        
    def most_featured_artist(self):
                
        tmp = []
        
        for index, track_dict in enumerate(self.playlist_json["tracks"]["items"]):
            for k, c in self.playlist_json["tracks"]["items"][index].items():
                if k == "track":
                    for ai, artist in enumerate(self.playlist_json["tracks"]["items"][index][k]["artists"]):
                        for i, j in self.playlist_json["tracks"]["items"][index][k]["artists"][ai].items():
                            if i == "name":
                                tmp.append(j)
                                continue
                            
        mfartist = tmp[0]
        max_occ = 0
        
        for artist in tmp:
            occurences = tmp.count(artist)
            if occurences > max_occ:
                max_occ = occurences
                mfartist = artist
                
        return mfartist, max_occ
    
    def most_featured_album(self):
        
        tmp = []
        
        for index, track_dict in enumerate(self.playlist_json["tracks"]["items"]):
            for k, c in self.playlist_json["tracks"]["items"][index].items():
                if k == "track":
                    for album_key, album_v in self.playlist_json["tracks"]["items"][index][k]["album"].items():
                        if album_key == "name" and album_v != "":
                            tmp.append(album_v)
                            continue
                            
        mfalbum = tmp[0]
        max_occ = 0
        
        for album in tmp:
            occurences = tmp.count(album)
            if occurences > max_occ:
                max_occ = occurences
                mfalbum = album
                
        return mfalbum, max_occ
    
    def is_song_in_playlist(self, song):
        song_to_check = Song(song)
        id_to_check = song_to_check.get_id()
        
        b = False
        
        for index, track_dict in enumerate(self.playlist_json["tracks"]["items"]):
            for k, c in self.playlist_json["tracks"]["items"][index].items():
                if k == "track":
                    if self.playlist_json["tracks"]["items"][index][k]["id"] == id_to_check:
                        b = True
                        break
                    
        return b
    
                    
# For the get playlist code, we need better OAuth code, let's work with a search query
def get_user_playlist(limit=50, offset=10):
    url = f"https://api.spotify.com/v1/me/playlists"
    headers = get_auth_header_cc()
    query = f"?limit={limit}&offset={offset}"
    
    query_url = url + query
    
    result = requests.get(url=query_url, headers=headers)
    
    json_result = json.loads(result.content)
    
    return json_result
    


if __name__ == "__main__":
    
    print("\n")
    
    playlist1 = Playlist(playlist_id="5KGUSMWkfWedc067zW7BYM")
    print(playlist1.get_playlist_name())
    playlist1.print_songs()    

    print("\n")
    
    print(playlist1.most_featured_artist())
    print(playlist1.most_featured_album())
    
    print(playlist1.is_song_in_playlist("Haan Main Galat"))
    print(playlist1.is_song_in_playlist("Haule Haule"))
    
    print("\n")

    
    song1 = Song(query_word="my darkest hours girl i felt so alone")
    print(song1.get_name())
    print(song1.get_artists())
    print(song1.get_id())
    


