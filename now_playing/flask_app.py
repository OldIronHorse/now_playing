from flask import Flask
from juice import connect, get_players, get_playing_track

app = Flask('now_playing')

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/players')
def players():
  server = connect('euterpe3')
  players = get_players(server)
  response = '';
  for player in players:
    response += '{}, {}\n'.format(player.name,player.id)
  return response
  
@app.route('/players/count')
def players_count():
  server = connect('euterpe3')
  return str(len(get_players(server)))

@app.route('/players/<name>')
def player_by_name(name):
  server = connect('euterpe3')
  players = [player for player in get_players(server) if player.name == name]
  track = get_playing_track(server,players[0].id)
  return '{}, {}, {}'.format(track.title,track.album,track.artist)
