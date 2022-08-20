#!/usr/bin/env python3

import json
import logging
import requests
import socket
import string, os, urllib, shlex
from subprocess import Popen, PIPE

CRED_FILE = '/root/.config/irssi_credentials'

LOG_FILE = '/var/log/notify'


def notify(channel, msg, to=None):
  with open(CRED_FILE) as f:
    config = json.load(f)
  creds = config[to] if to is not None else config[config['default_user']]
  notifier = IrssiNotifier(creds['token'], creds['password'])
  notifier.send(msg, chan='#%s' % channel, nick=socket.gethostname())


class IrssiNotifier(object):

  def __init__(self, api_token, enc_pass):
    self.api_token = api_token
    self.enc_pass = enc_pass

  def encrypt(self, text):
    command = 'openssl enc -aes-128-cbc -salt -base64 -md md5 -A -pass env:OpenSSLEncPW'
    opensslenv = os.environ.copy()
    opensslenv['OpenSSLEncPW'] = self.enc_pass
    output, errors = Popen(
        shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=PIPE,
        env=opensslenv).communicate(str.encode(text + ' '))
    output = output.decode('utf-8')
    output = output.replace('/', '_')
    output = output.replace('+', '-')
    output = output.replace('=', '')
    return output

  def send(self, message, chan='#local', nick='server'):
    data = {
      'apiToken': self.api_token,
      'nick': self.encrypt(nick),
      'channel': self.encrypt(chan),
      'message': self.encrypt(message),
      'version': 24,
    }
    url = 'https://irssinotifier.appspot.com/API/Message'
    logging.info('Now sending message to irssinotifier API.')
    resp = requests.post(url, data=data)
    logging.info('Message sent: %s', resp)


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
  logging.info('Sending notification to channel "%s":\n%s' % (chan, msg))
  notify(chan, msg)
  sys.exit(0)
