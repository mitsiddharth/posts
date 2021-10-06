import argparse
import json
import os
from pathlib import Path
import matplotlib.pyplot as plt


def get_all_scoring_info():
  ret = []
  for p in Path(DIR_PREFIX).rglob('scoring_*.json'):
    ret.append(p)
  return ret

arg_parser = argparse.ArgumentParser(description='Nelson analysis in IPL scorecards.')
arg_parser.add_argument('--dir_prefix', type=str, help='Prefix of path to directory where scorecard data resides.',
        required=True)

args = arg_parser.parse_args()

# Note about the directory structure and filenames:
# =================================================
# * The --dir_prefix command-line argument should point to the scorecard info.
# * Each match's information should be in a file by itself.
# * The filename should be of the format "scoring_<match_id>.json", where
#   <match_id> is a unique integer.
DIR_PREFIX = args.dir_prefix

fow_at_run = {}
fow_at_ball = {}

total_num_wickets = 0

for info in get_all_scoring_info():
  data = json.loads(open(info).read())
  for inning in data['innings']:
    fow = inning['scorecard']['fow']
    if fow:
      for f in fow:
        runs = f['r']
        balls = (f['bp']['over'] - 1)*6 + f['bp']['ball']
        if runs not in fow_at_run: fow_at_run[runs] = 0
        if balls not in fow_at_ball: fow_at_ball[balls] = 0
        fow_at_run[runs] += 1
        fow_at_ball[balls] += 1
        total_num_wickets += 1


print('Total number of wickets: ', total_num_wickets)
x = []
values = []

for k in fow_at_run:
  x.append(k)
  values.append(fow_at_run[k])

highlighted_scores = [0, 111, 222, 127]
highlighted_balls = [111]

plt.bar(x, values)
for _x in highlighted_scores:
  plt.bar(_x, fow_at_run[_x], color='red')
plt.xlabel('Frequency of wickets')
plt.ylabel('Number of runs')
plt.title('Frequency of wickets per runs scored')
plt.show()

ball_x = []
ball_values = []
for k in fow_at_ball:
  ball_x.append(k)
  ball_values.append(fow_at_ball[k])

plt.bar(ball_x, ball_values)
for _x in highlighted_balls:
  plt.bar(_x, fow_at_ball[_x], color='red')
plt.xlabel('Frequency of wickets')
plt.ylabel('Ball number')
plt.title('Frequency of wickets per ball number')
plt.show()
