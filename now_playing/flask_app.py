from flask import Flask, jsonify, render_template, request, session, redirect,\
  url_for, flash
from juice import connect, get_players, get_playing_track, get_artists, state,\
  play, pause, get_player_name, get_current_playlist, get_player_volume,\
  set_player_volume, get_albums, get_tracks, get_genres, get_years,\
  player_playlist_play

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
  SECRET_KEY='develeopment key',
  SERVER='euterpe3',
  MQTT_BROKER_HOST='euterpe3',
  MQTT_BROKER_PORT=1884,
  USERNAME='default',
  PASSWORD='password'))
app.config.from_envvar('NOW_PLAYING_SETTINGS', silent=True)

### start multipage site ###

@app.route('/mqtt')
def mqtt_poc():
  return render_template('mqtt_poc.html', 
                          mqtt_broker_host=app.config['MQTT_BROKER_HOST'],
                          mqtt_broker_port=app.config['MQTT_BROKER_PORT'])

@app.route('/library')
def library_page():
  return render_template('library.html')

@app.route('/library/artists')
def artists_page():
  server = connect(app.config['SERVER'])
  artists = get_artists(server)
  server.close()
  return render_template('artists.html',
                         artists=artists)

@app.route('/library/artists/<artist_id>')
def artist_page(artist_id):
  server = connect(app.config['SERVER'])
  artist = get_artists(server, artist_id=artist_id)[0]
  albums = get_albums(server, artist_id=artist_id)
  server.close()
  return render_template('artist.html', albums=albums, artist=artist)

@app.route('/library/albums')
def albums_page():
  server = connect(app.config['SERVER'])
  albums = get_albums(server)
  server.close()
  return render_template('albums.html', albums=albums)

@app.route('/library/albums/<album_id>')
def album_page(album_id):
  server = connect(app.config['SERVER'])
  album = get_albums(server, album_id=album_id)[0]
  artist = get_artists(server, artist_id=album['artist_id'])[0]
  tracks = get_tracks(server, album_id=album_id)
  tracks.sort(key=lambda track: track['tracknum'])
  server.close()
  return render_template('album.html', artist=artist, album=album, tracks=tracks)

@app.route('/library/tracks')
def tracks_page():
  server = connect(app.config['SERVER'])
  tracks = get_tracks(server)
  server.close()
  return render_template('tracks.html', tracks=tracks)

@app.route('/library/tracks/<track_id>')
def track_page(track_id):
  server = connect(app.config['SERVER'])
  track = get_tracks(server, track_id=track_id)[0]
  server.close()
  return render_template('track.html', track=track)
  
@app.route('/library/genres')
def genres_page():
  server = connect(app.config['SERVER'])
  genres = get_genres(server)
  server.close()
  return render_template('genres.html', genres=genres)
  
@app.route('/library/genres/<genre_id>')
def genre_page(genre_id):
  server = connect(app.config['SERVER'])
  genre = [g for g in get_genres(server) if g['id'] == int(genre_id)][0]
  artists = get_artists(server, genre_id=genre_id)
  server.close()
  return render_template('genre.html', genre=genre, artists=artists)

@app.route('/library/years')
def years_page():
  server = connect(app.config['SERVER'])
  years = get_years(server)
  server.close()
  return render_template('years.html', years=years)

@app.route('/library/years/<year>')
def year_page(year):
  server = connect(app.config['SERVER'])
  albums = get_albums(server, year=year)
  server.close()
  return render_template('year.html', year=year, albums=albums)

@app.route('/library/new music')
def new_music_page():
  server = connect(app.config['SERVER'])
  albums = get_albums(server, sort='new')
  server.close()
  return render_template('new_music.html', albums=albums)

### Start single page app ###

@app.route('/')
def single_page_app():
  return render_template('single_page.html',
                          mqtt_broker_host=app.config['MQTT_BROKER_HOST'],
                          mqtt_broker_port=app.config['MQTT_BROKER_PORT'])
  
### Start web services ###

@app.route('/api/library/artists')
def library_artists():
  server = connect(app.config['SERVER'])
  artists = get_artists(server)
  server.close()
  return jsonify(artists)

@app.route('/api/library/albums')
def library_albums():
  server = connect(app.config['SERVER'])
  albums = get_albums(server, **{k: request.args[k] for k in request.args.keys()})
  server.close()
  return jsonify(albums)

@app.route('/api/library/albums/<album_id>')
def library_album_by_id(album_id):
  server = connect(app.config['SERVER'])
  albums = get_albums(server, album_id=album_id)
  server.close()
  return jsonify(albums[0])

@app.route('/api/library/tracks')
def library_tracks():
  server = connect(app.config['SERVER'])
  tracks = get_tracks(server, **{k: request.args[k] for k in request.args.keys()})
  server.close()
  return jsonify(tracks)

@app.route('/api/players/<player_id>/playlist/play', methods=['POST'])
def player_playlist(player_id):
  print('player_playlist:', request.get_json())
  type = request.get_json()['type']
  id = request.get_json()['id']
  server = connect(app.config['SERVER'])
  track = get_tracks(server, page_size=1, track_id=id)[0]
  print('player_playlist: track:', track)
  player_playlist_play(server, player_id, track['url'])
  server.close()
  #TODO: return updated playlist?
  return 'OK'
  

#TODO:html interface
#TODO:js interface?

#TODO: cache library at startup and cache in python dictionaries
#TODO: index library cache
#TODO: mark all library query results as cacheable
#TODO: What (if any) cacheing is appropriate for player and playlist queries?
