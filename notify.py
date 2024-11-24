#!/usr/bin/env python3

import json
import logging
import os
import requests

CONFIG_FILE = '/root/.config/notify.json'

LOG_FILE = '/var/log/notify'

def notify(channel, msg, to=None):
  with open(CONFIG_FILE) as f:
    config = json.load(f)
    
  header = {"title": "[ %s ]" % config["name"], "subtitle": "Channel: %s" % channel}
  widget = {"textParagraph": {"text": msg}}
  cards = [
      {
          "header": header,
          "sections": [{"widgets": [widget]}],
      },
  ]
  return requests.post(config["webhook_url"], json={"cards": cards})


if __name__ == '__main__':
  import sys
  if len(sys.argv) < 3:
    print('Usage: ./notify.py [channel] [message]')
    sys.exit(1)

  logging.basicConfig(
      filename=LOG_FILE, level=logging.DEBUG,
      format=('%(asctime)s.%(msecs)d %(levelname)s %(module)s - %(funcName)s: '
              '%(message)s'),
      datefmt='%Y-%m-%d %H:%M:%S')

  chan = sys.argv[1]
  msg = sys.argv[2]
  if os.path.isfile(msg):
    logging.info('Loading message from file %s' % msg)
    with open(msg) as f:
      msg = f.read()
  TRUNC = 1000
  msg = msg[:TRUNC]
  if len(msg) == TRUNC:
      msg = msg + " ...truncated"
  logging.info('Sending notification to channel "%s":\n%s' % (chan, msg))
  notify(chan, msg)
  sys.exit(0)
