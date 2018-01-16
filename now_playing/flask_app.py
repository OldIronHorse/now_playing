from flask import Flask, jsonify, render_template, request, session, redirect,\
  url_for, flash
from juice import connect, get_players, get_playing_track, get_artists, state,\
  play, pause, get_player_name, get_current_playlist, get_player_volume,\
  set_player_volume, get_albums, get_tracks, get_genres, get_years

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

@app.route('/')
def show_players():
  server = connect(app.config['SERVER'])
  players = get_players(server)
  server.close()
  return render_template('show_players.html', players=players)

@app.route('/login', methods=['GET','POST'])
def login():
  error = None
  if request.method == 'POST':
    if request.form['username'] != app.config['USERNAME'] \
        or request.form['password'] != app.config['PASSWORD']:
      error = 'Invalid credentials'
    else:
      session['logged_in'] = True
      flash('You are logged in')
      return redirect(url_for('show_players'))
  return render_template('login.html', error=error)

@app.route('/logout')
def logout():
  session.pop('logged_in',None)
  flash('You were logged out')
  return redirect(url_for('show_players'))

@app.route('/player/<player_id>')
def player(player_id):
  action = request.args.get('action')
  if action:
    actions = {'play': play, 'pause': pause}
    server = connect(app.config['SERVER'])
    actions[action](server, player_id)
    server.close()
    return redirect(url_for('player', player_id=player_id))
  else:
    server = connect(app.config['SERVER'])
    name = get_player_name(server, player_id)
    track = get_playing_track(server, player_id)
    player_state = state(server, player_id)
    playlist = get_current_playlist(server, player_id)
    server.close()
    available_action = {'play': 'pause', 'pause': 'play', 'stop': 'play'}
    return render_template('player.html', track=track, player_name=name,
      player_id=player_id, action=available_action[player_state],
      playlist=playlist)

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
  
### Start service POC ###

@app.route('/players/<player_id>', methods=['GET','PATCH'])
def player_state(player_id):
  server = connect(app.config['SERVER'])
  if request.method == 'PATCH':
    new_state = request.get_json()
    actions = {'play': play, 'pause': pause}
    try:
      actions[new_state['state']](server, player_id)
    except KeyError:
      pass
    try:
      set_player_volume(server, player_id, new_state['volume'])
    except KeyError:
      pass
  player_name = get_player_name(server, player_id)
  current_track = get_playing_track(server, player_id)
  player_state = state(server, player_id)
  player_volume = get_player_volume(server, player_id)
  server.close()
  return jsonify({'state': player_state,
                  'volume': player_volume,
                  'name': player_name,
                  'id': player_id,
                  'current_track':{'title': current_track.title,
                                   'album': current_track.album,
                                   'artist': current_track.artist}})
    

@app.route('/players')
def players():
  server = connect(app.config['SERVER'])
  players = get_players(server)
  server.close()
  response = '';
  for player in players:
    response += '{}, {}\n'.format(player.name,player.id)
  return response
  
@app.route('/players/count')
def players_count():
  server = connect(app.config['SERVER'])
  players = get_players(server)
  server.close()
  return str(len(players))

@app.route('/players/<name>/now_playing')
def player_by_name(name):
  server = connect(app.config['SERVER'])
  players = [player for player in get_players(server) if player.name == name]
  track = get_playing_track(server,players[0].id)
  server.close()
  return '{}, {}, {}'.format(track.title,track.album,track.artist)

@app.route('/library/artists')
def library_artists():
  server = connect(app.config['SERVER'])
  artists = get_artists(server)
  server.close()
  return jsonify([artist._asdict() for artist in artists])

#TODO:html interface
#TODO:js interface?

#TODO: cache library at startup and cache in python dictionaries
#TODO: index library cache
#TODO: mark all library query results as cacheable
#TODO: What (if any) cacheing is appropriate for player and playlist queries?
