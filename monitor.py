#!/usr/bin/python
# -*- coding: utf-8 -*-

import signal
import sys
import argparse
import curses
import mosquitto

parser = argparse.ArgumentParser(description='Monitors a mosquitto MQTT broker.')
parser.add_argument("--host", default='localhost',
                   help="mqtt host to connect to. Defaults to localhost.")
parser.add_argument("-p", "--port", type=int, default=1883,
                   help="network port to connect to. Defaults to 1883.")
parser.add_argument("-k", "--keepalive", type=int, default=60,
                   help="keep alive in seconds for this client. Defaults to 60.")

args = parser.parse_args()

# Totals
SYS_BYTES_RECEIVED = "$SYS/broker/bytes/received"
SYS_BYTES_SENT = "$SYS/broker/bytes/sent"
SYS_MESSAGES_DROPPED = "$SYS/broker/messages/dropped"
SYS_MESSAGES_RECEIVED = "$SYS/broker/messages/received"
SYS_MESSAGES_SENT = "$SYS/broker/messages/sent"

# Average
SYS_LOAD_BYTES_RECEIVED = "$SYS/broker/load/bytes/received/1min"
SYS_LOAD_BYTES_SENT = "$SYS/broker/load/bytes/sent/1min"
SYS_LOAD_PUBLISHED_RECEIVED = "$SYS/broker/load/publish/received/1min"
SYS_LOAD_PUBLISHED_SENT = "$SYS/broker/load/publish/sent/1min"

topics = [
  SYS_BYTES_RECEIVED,
  SYS_BYTES_SENT,
  SYS_MESSAGES_DROPPED,
  SYS_MESSAGES_RECEIVED,
  SYS_MESSAGES_SENT,
  SYS_LOAD_BYTES_RECEIVED,
  SYS_LOAD_BYTES_SENT,
  SYS_LOAD_PUBLISHED_RECEIVED,
  SYS_LOAD_PUBLISHED_SENT
]

stats = {}

flags = {
  "connected": False
}

screen = curses.initscr()
curses.noecho()
curses.curs_set(0) 
screen.keypad(1)
screen.timeout(10)

def draw():
  
  receivedMb = float(stats.get(SYS_BYTES_RECEIVED, 0.0)) / 1024.0 / 1024.0
  sentMb = float(stats.get(SYS_BYTES_SENT, 0.0)) / 1024.0 / 1024.0
  
  receivedKbps = float(stats.get(SYS_LOAD_BYTES_RECEIVED, 0.0)) / 1024.0 / 60.0
  sentKbps = float(stats.get(SYS_LOAD_BYTES_SENT, 0.0)) / 1024.0 / 60.0
  
  screen.clear()
  screen.addstr(1,2, "Mosquitto Stats")
  screen.addstr(2,2, "Connected: %s (%s:%d, %d)" % ( ("Yes" if flags["connected"] else "No"), args.host, args.port, args.keepalive ))
  screen.addstr(5,2, "         |  Received\t\tSent\t\tReceived/min\t\tSent/min")
  screen.addstr(6,2, "-------------------------------------------------------------------------------")
  screen.addstr(7,2, "Bytes    |  %.2f Mb\t\t%.2f Mb\t\t%.2f kbps\t\t%.2f kbps" % (receivedMb, sentMb, receivedKbps, sentKbps ))    
  screen.addstr(8,2, "Messages |  %s\t\t%s\t\t%s\t\t%s" % (stats.get(SYS_MESSAGES_RECEIVED), stats.get(SYS_MESSAGES_SENT), stats.get(SYS_LOAD_PUBLISHED_RECEIVED), stats.get(SYS_LOAD_PUBLISHED_SENT) ))    
  screen.addstr(11,2, "Messages dropped: %s" % stats.get(SYS_MESSAGES_DROPPED))
  screen.addstr(13,2, "Press 'q' to quit")

def signal_handler(signal, frame):
  curses.endwin()
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def on_connect(mosq, obj, rc):
  flags["connected"] = True
  draw()
  for topic in topics:
    mosq.subscribe(topic, 0)
    
def on_disconnect(mosq, obj, rc):
  flags["connected"] = False
  draw()

def on_message(mosq, obj, msg):
  stats[msg.topic] = str(msg.payload)
  draw()

def on_log(mosq, obj, level, string):
  print(string)

mqttc = mosquitto.Mosquitto()

# Register callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
#mqttc.on_log = on_log

# Connect on start
mqttc.connect(args.host, args.port, args.keepalive)

draw()

while True:
  
  rc = mqttc.loop()
  if rc != 0: break
  
  event = screen.getch()
  
  if event == ord("q"): break
  elif event == ord("c"): 
    mqttc.connect("127.0.0.1")
  elif event == ord("d"):
    mqttc.disconnect()
  
  draw()

curses.endwin()
