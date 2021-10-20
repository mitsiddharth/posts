import csv
import numpy as np
import argparse
from pathlib import Path
from prettytable import PrettyTable

def get_spin_angle_paths(dir_prefix):
  ret = []
  for path in Path(dir_prefix).rglob('spin_angle_*'):
    ret.append(path)
  return ret

def is_spinner(bowling_style):
  return bowling_style in ['OFF_SPIN', 'LEG_SPIN', 'ORTHODOX', 'UNORTHODOX']

def get_match_id(path):
  tokens = str(path).split('/')
  filename = tokens[-1]
  assert(filename.startswith('spin_angle_'))
  match_id_str = tokens[-1].replace('.json', '').split('_')[-1]
  assert(match_id_str.isdigit())
  return int(match_id_str)

def is_natural_spin(bowling_style, spin_angle):
  if bowling_style == 'LEG_SPIN':
    return spin_angle < 0
  if bowling_style == 'OFF_SPIN':
    return spin_angle > 0
  if bowling_style == 'ORTHODOX':
    return spin_angle < 0
  if bowling_style == 'UNORTHODOX':
    return spin_angle > 0
  assert(False) # Unspupported bowling_style
  return False  # this will not be reached.

def load_player_db(path):
  player_db = {}
  header = True
  with open(path) as f:
    reader = csv.reader(f)
    for r in reader:
      if header:
        header = False
        continue
      player_id = int(r[0])
      player_db[player_id] = r
  return player_db


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--dir_prefix', type=str, required=True, help='Directory prefix where spin_angle* files are present')
arg_parser.add_argument('--player_db_csv', type=str, required=True, help='Path to csv-file containing player database.')
arg_parser.add_argument('--balls_bowled_threshold', type=int, required=True, help='Only bowlers who bowled at least these many balls '
        'will be considered for the analysis.')

args = arg_parser.parse_args()

bowlers_data = {}

data = {}

for f in get_spin_angle_paths(args.dir_prefix):
  match_id = get_match_id(f)
  with open(f) as csvfile:
    header = True
    reader = csv.reader(csvfile)
    for r in reader:
      if header:
        header = False
        continue
      key = r[0]
      data_key = '%(match_id)d.%(key)s' % locals()
      data[data_key] = r

data_by_bowler = {}

for k in data:
  r = data[k]
  key = r[0]
  bowler = int(r[1])
  striker = int(r[2])
  is_rhb = True if r[3] == 'y' else False
  speed = float(r[4])
  is_dismissal = True if r[5] == 'y' else False
  runs = int(r[6])
  spin_angle = float(r[7])
  bowling_style = r[8]
  if not is_spinner(bowling_style): continue
  if bowler not in data_by_bowler: data_by_bowler[bowler] = []
  if is_natural_spin(bowling_style, spin_angle):
    data_by_bowler[bowler].append(k)

avg_spin_by_bowler = {}

avg_spin_arr = []
for bowler in data_by_bowler:
  angles_arr = []
  bowling_style = ''
  for k in data_by_bowler[bowler]:
    r = data[k]
    key = r[0]
    bowler = int(r[1])
    striker = int(r[2])
    is_rhb = True if r[3] == 'y' else False
    speed = float(r[4])
    is_dismissal = True if r[5] == 'y' else False
    runs = int(r[6])
    spin_angle = float(r[7])
    bowling_style = r[8] 
    angles_arr.append(spin_angle)
  if not angles_arr: continue
  avg_spin = np.average(angles_arr)
  avg_spin_arr.append([bowler, avg_spin])

avg_spin_arr.sort(key=lambda x: -abs(x[1]))

player_db = load_player_db(args.player_db_csv)

table_by_style = {}

for [bowler, avg_spin] in avg_spin_arr:
  num_balls = len(data_by_bowler[bowler])
  fields = player_db[bowler]
  bowling_style = fields[6]
  if bowling_style not in table_by_style:
    table_by_style[bowling_style] = PrettyTable()
    table_by_style[bowling_style].field_names = ['Bowler', 'Bowling Style', 'Avg spin', 'Num balls']
  table = table_by_style[bowling_style]
  if num_balls < args.balls_bowled_threshold: continue
  table.add_row([fields[1], fields[6], '%0.2f' % (abs(avg_spin)), num_balls])

for style in ['LEG_SPIN', 'OFF_SPIN', 'ORTHODOX', 'UNORTHODOX']:
  table = table_by_style[style]
  table.align['Bowler'] = 'l'
  table.align['Bowling Style'] = 'l'
  table.align['Avg spin'] = 'r'
  table.align['Num balls'] = 'r'
  print(table)
