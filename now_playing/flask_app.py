from flask import Flask, jsonify
from juice import connect, get_players, get_playing_track, get_artists

app = Flask('now_playing')

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/players')
def players():
  server = connect('euterpe3')
  players = get_players(server)
  server.close()
  response = '';
  for player in players:
    response += '{}, {}\n'.format(player.name,player.id)
  return response
  
@app.route('/players/count')
def players_count():
  server = connect('euterpe3')
  players = get_players(server)
  server.close()
  return str(len(players))

@app.route('/players/<name>/now_playing')
def player_by_name(name):
  server = connect('euterpe3')
  players = [player for player in get_players(server) if player.name == name]
  track = get_playing_track(server,players[0].id)
  server.close()
  return '{}, {}, {}'.format(track.title,track.album,track.artist)

@app.route('/library/artists')
def library_artists():
  server = connect('euterpe3')
  artists = get_artists(server)
  server.close()
  return jsonify([artist._asdict() for artist in artists])

#TODO: cache library at startup and cache in python dictionaries
#TODO: index library cache
#TODO: mark all library query results as cacheable
#TODO: What (if any) cacheing is appropriate for player and playlist queries?
