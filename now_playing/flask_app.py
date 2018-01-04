from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash
from juice import connect, get_players, get_playing_track, get_artists

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
  SECRET_KEY='develeopment key',
  SERVER='euterpe3',
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
    print(repr(request.form))
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

### Start service POC ###

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
