from flask import Flask, jsonify, render_template, request, session, redirect,\
  url_for, flash
from flask_cors import CORS
from juice import connect, get_players, get_playing_track, get_artists, state,\
  play, pause, get_player_name, get_current_playlist, get_player_volume,\
  set_player_volume, get_albums, get_tracks, get_genres, get_years,\
  player_playlist_control, player_playlist_delete, status, previous_track,\
  next_track

app = Flask(__name__)
CORS(app)
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

  ### start library services ###

@app.route('/api/library/artists')
def library_artists():
  server = connect(app.config['SERVER'])
  artists = get_artists(server)
  server.close()
  return jsonify(artists)

@app.route('/api/library/artists/<id>')
def library_artist_by_id(id):
  server = connect(app.config['SERVER'])
  artists = get_artists(server, artist_id=id)
  server.close()
  return jsonify(artists[0])

@app.route('/api/library/albums')
def library_albums():
  server = connect(app.config['SERVER'])
  albums = get_albums(server, **{k: request.args[k] for k in request.args.keys()})
  server.close()
  print('library_albums()', jsonify(albums).data[16500:16700])
  return jsonify(albums)

@app.route('/api/library/albums/<album_id>')
def library_album_by_id(album_id):
  server = connect(app.config['SERVER'])
  albums = get_albums(server, album_id=album_id)
  server.close()
  #print('library_album_by_id(', album_id, ')', albums[0])
  return jsonify(albums[0])

@app.route('/api/library/tracks')
def library_tracks():
  server = connect(app.config['SERVER'])
  tracks = get_tracks(server, **{k: request.args[k] for k in request.args.keys()})
  server.close()
  #print('library_tracks:', tracks)
  return jsonify(tracks)

@app.route('/api/library/years')
def library_years():
  server = connect(app.config['SERVER'])
  years = get_years(server)
  server.close()
  return jsonify(years)

  ### start player services ###

type_to_id_tag = {
  'track': 'track_id',
  'album': 'album_id',
  'artist': 'artist_id',
}

@app.route('/api/players')
def players():
  server = connect(app.config['SERVER'])
  players = get_players(server)
  server.close()
  return jsonify(players)

@app.route('/api/players/<player_id>')
def player(player_id):
  server = connect(app.config['SERVER'])
  players = status(server, player_id)
  server.close()
  return jsonify(players)

modes = {
  'play': play,
  'pause': pause,
}
@app.route('/api/players/<player_id>/mode', methods=['PUT'])
def player_mode(player_id):  
  json = request.get_json()
  print('player_mode:', request)
  print('player_mode:', json)
  server = connect(app.config['SERVER'])
  modes[json['mode']](server, player_id)
  server.close()
  return ('', 204)

@app.route('/api/players/<player_id>/volume', methods=['PUT'])
def player_volume(player_id):
  json = request.get_json()
  print('player_mode:', request)
  print('player_mode:', json)
  server = connect(app.config['SERVER'])
  set_player_volume(server, player_id, '{0:+}'.format(json['delta']))
  server.close()
  return ('', 204)
  
@app.route('/api/players/<player_id>/playlist_current_index', methods=['PUT'])
def player_playlist_current_index(player_id):
  json = request.get_json()
  print('player_mode:', request)
  print('player_mode:', json)
  server = connect(app.config['SERVER'])
  if json['delta'] < 0:
    previous_track(server, player_id)
  elif json['delta'] > 0:
    next_track(server, player_id)
  server.close()
  return ('', 204)

@app.route('/api/players/<player_id>/playlist/tracks', methods=['PUT','POST'])
def player_playlist_tracks(player_id):
  method_to_command = {
    'PUT': 'load',
    'POST': 'add',
  }
  json = request.get_json()
  server = connect(app.config['SERVER'])
  player_playlist_control(server, player_id, method_to_command[request.method],
    **{type_to_id_tag[json['type']]: json['id']})
  new_player_status = status(server, player_id)['player']
  server.close()
  return jsonify(new_player_status['playlist'])

@app.route('/api/players/<player_id>/playlist/tracks/<index>', methods=['DELETE'])
def player_playlist_tracks_indexed(player_id, index):
  server = connect(app.config['SERVER'])
  player_playlist_delete(server, player_id, index)
  server.close()
  return ('', 204)

#TODO: cache library at startup and cache in python dictionaries
#TODO: index library cache
#TODO: mark all library query results as cacheable
#TODO: What (if any) cacheing is appropriate for player and playlist queries?
