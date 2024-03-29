# This is the Flask app

# From the backend files
from functions import (
    what_playlist_what_song, 
    create_monthly_array, 
    random_playlist_obj, 
    top_task1, 
    top_task2)
from backend import Song 

# Imports from flask
from flask import Flask, render_template, request, redirect, jsonify, session

# For the client ID and client Secret
import secrets 
from dotenv import load_dotenv 
import os
import base64

# For the API calls within OAuth 2.0
import requests 
import urllib.parse
import json

# For time
from datetime import datetime

# For random webpage
import random

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

MONTHLY_PLAYLISTS = create_monthly_array()

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URL = "http://localhost:5000/callback"

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"


@app.route("/")
def index():
        
    return render_template("index.html")

@app.route("/check", methods=["POST", "GET"])
def check(monthly_playlists = MONTHLY_PLAYLISTS):
    
    if request.method == "POST":
    
        song_name = str(request.form["song_input"])
        song_to_find = Song(song_name)
        
        song_name = song_to_find.get_name()
        song_artists_list = song_to_find.get_artists()
        song_artists = ""
        
        if len(song_artists_list) == 1:
            song_artists = song_artists_list[0]
        else:
            for index, artist in enumerate(song_artists_list):
                song_artists += artist
                if index < len(song_artists_list) - 1:
                    song_artists += ", "
        
        song_image_url = song_to_find.get_image_url()
        song_link_url = song_to_find.get_song_url()
        
        message1 = f"""
        Song Name: {song_name}
        """
        message_new = f"""
        \n Song Artists: {song_artists}
        """
            
        song_check, play_url = what_playlist_what_song(song_to_find)
        
        audio_message = ""
        playback_link = song_to_find.get_playback()
        
        if playback_link != None:
            audio_message = f"""
            <audio src='{song_to_find.get_playback()}' controls loop preload = 'metadata'>
            
            </audio>
            
            """    
        
            
        return render_template(
                "check.html",
                message1 = message1,
                message_new = message_new,
                naval = song_check,
                song_image_url=song_image_url,
                song_link_url=song_link_url,
                play_url=play_url,
                audio=audio_message
            )
    
    else:
        return render_template("index.html")
        
@app.route('/login')
def login():
    
    print("\n I'm at login.")
    
    scope = "ugc-image-upload playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-top-read"
    
    # remove show_dialog during execution
    params = {
        'client_id' : CLIENT_ID,
        'response_type' : 'code',
        'scope' : scope,
        'redirect_uri' : REDIRECT_URL,
        'show_dialog' : True
    }
    
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    
    print(f"\n Here's the Auth URL: {auth_url}")
    
    return redirect(auth_url)

@app.route('/callback')
def callback():
    
    print("\n I'm at callback")
    
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        
        req_body = {
            'code' : request.args['code'],
            'grant_type' : 'authorization_code',
            'redirect_uri' : REDIRECT_URL,
            'client_id' : CLIENT_ID,
            'client_secret' : CLIENT_SECRET            
        }
        
        print(f"\n Here's the request body {req_body}")
        
        response = requests.post(url=TOKEN_URL, data=req_body)
        token_info = response.json()
        
        print("\n Here's the JSON response for Token")
        print(token_info)
        
        session["access_token"] = token_info["access_token"]
        session["refresh_token"] = token_info["refresh_token"]
        session["expires_at"] = datetime.now().timestamp() + token_info["expires_in"]
        
        print(f"\n Here's the access token {session['access_token']}")
        print(f"\n Here's the refresh token {session['refresh_token']}")
        print(f"\n Here's the expires at {session['expires_at']}")
        
        return redirect('/')
    
@app.route('/playlists')
def get_playlists():
    
    print("\n I'm at playlists")
    
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session["expires_at"]:
        return redirect('/refresh-token')
    
    if 'access_token' in session or datetime.now().timestamp() > session["expires_at"]:
        
        print(f"\n AGAIN Here's the access token {session['access_token']}")
        print(f"\n AGAIN Here's the refresh token {session['refresh_token']}")
        print(f"\n AGAIN Here's the expires at {session['expires_at']}")
        
        try:
    
            headers = {
                'Authorization' : f"Bearer {session['access_token']}"
            }
            
            print(f"\n Here's the headers {headers}")
                                    
            result_0 = requests.get(url=f"https://api.spotify.com/v1/me/playlists?limit=1&offset=0", headers=headers)
            
            print("\n Here's the response_0 status code")
            print(result_0.status_code)
            
            print("\n Here's the response_0 content")
            print(result_0.content)
            
            playlists_0 = result_0.json()
            
            total_playlists = int(playlists_0["total"])
            
            random_integer = random.randint(0, total_playlists-1)

            print("I'm on the while loop :(")
            print(f"\n I'm the random integer for now {random_integer}")
            result = requests.get(url=f"https://api.spotify.com/v1/me/playlists?limit=1&offset={random_integer}", headers=headers)
            playlists = result.json()
            
            print("/n Here's the JSON file")
            print(playlists)
            
            random_playlist = random_playlist_obj(playlists)
            
            name = random_playlist.get_playlist_name()
            user = random_playlist.get_playlist_owner()
            link = random_playlist.get_playlist_url()
            
            artist_n, n1 = random_playlist.most_featured_artist()
            album_n, n2 = random_playlist.most_featured_album()
            
            avg_pop, most_pop, n3, least_pop, n4 = random_playlist.popularity()
            
            avg_du, most_du, n5, least_du, n6 = random_playlist.duration()
            
            image_code = ""
            if random_playlist.get_playlist_image():
                image_code = f"""
                <a href='{link}' target='_blank'>
                    <img src = '{random_playlist.get_playlist_image()}' alt = 'Playlist Image'>
                </a>
                """
                
            if name == "Error":
                
                return redirect('/playlists')
                
                    
            return render_template(
                "randomplay.html",
                playlist_name=name,
                user_name=user,
                playlist_link=link,
                image_code=image_code,
                artist_name=artist_n,
                n1=n1,
                album_name=album_n,
                n2=n2,
                avg_pop=avg_pop,
                most_pop=most_pop,
                n3=n3,
                least_pop=least_pop,
                n4=n4,
                avg_du=avg_du,
                most_du=most_du,
                n5=n5,
                least_du=least_du,
                n6=n6
                )
            
        except json.JSONDecodeError as e:
            return jsonify({"error" : f"JSON decoding failed: {str(e)}"})
        
        except requests.exceptions.RequestException as e:
            return jsonify({"error" : f"Request failed: {str(e)}"})
        
        except Exception as e:
            return jsonify({"error" : f"An unexpected error occures: {str(e)}"})
        
    else:
        return jsonify({"HELLO" : "I NEED HELP"})
        
@app.route('/refesh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session["expires_at"]:
        req_body = {
            'grant_type' : 'refresh_token',
            'refresh_token' : session['refresh_token']
        }
        
        auth_string = CLIENT_ID + ":" + CLIENT_SECRET
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
        
        header = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type" : "application/x-www-form-urlencoded"
        }
        
        result = requests.post(url=AUTH_URL, headers=header, data=req_body)
        
        new_token_info = result.json()
        
        session["access_token"] = new_token_info["access_token"]
        session["expires_at"] = datetime.now().timestamp() + new_token_info["expires_in"]
        
        return redirect('/playlist')
    
@app.route('/wrap')
def wrapp():
    return render_template("wrapp.html")
            
@app.route('/wrapped', methods=["POST", "GET"])
def wrapped():

    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session["expires_at"]:
        return redirect('/refresh-token')
    
    if 'access_token' in session or datetime.now().timestamp() > session["expires_at"]:
        
        if request.method == "POST":
            
            top_var = int(request.form['top_type'])
            search_type = int(request.form['search_type'])
            time_var = int(request.form['time_type'])
            
            print(f"\n I'm the top value: {top_var}")
            print(f"\n I'm the search value: {search_type}")
            print(f"\n I'm the time value: {time_var}")
            
            
            try:
            
                headers = {
                                'Authorization' : f"Bearer {session['access_token']}"
                            }
                
                print(f"\n For the third time I'm the headers: {headers}")
                
                msg, requrl = top_task1(top=top_var, search=search_type, time=time_var)
                
                print(f"\nI'm the URL {requrl}")
                
                result = requests.get(url=requrl, headers=headers)
                
                                
                print(f"\nI'm the result content: \n {result.content}")
                print(f"\nI'm the result status code: \n {result.status_code}")
                
                json_file = result.json()
                
                html_text = top_task2(json_file)
                
                return render_template(
                    "wrapped.html",
                    message_top=msg,                    
                    top_list=html_text
                )
                
                
            except Exception as e:
                
                return jsonify({"error" : f"An unexpected error occured: {str(e)}"})
            
        else:
            
            return render_template("wrapped.html")

@app.route('/recommender', methods=["POST", "GET"])
def recommender():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session["expires_at"]:
        return redirect('/refresh-token')
    
    if 'access_token' in session or datetime.now().timestamp() > session["expires_at"]:
        pass
        
        

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)