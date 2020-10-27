#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time, vk, threading, os, socket, re, sys, traceback, json, sqlite3
from utils import *

info = load_json('info.json')
mrproper_time = time.time()

msgdb = sqlite3.connect('messages.db')
msgdb_cur = msgdb.cursor()

deldb = sqlite3.connect('deleted.db')
deldb_cur = deldb.cursor()

msgdb_cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='messages' ''')
if msgdb_cur.fetchone()[0] != 1:
	msgdb_cur.execute('CREATE TABLE messages(id INTEGER, time BIGINT, msg STRING)')
	msgdb.commit()

deldb_cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='messages' ''')
if deldb_cur.fetchone()[0] != 1:
	deldb_cur.execute('CREATE TABLE messages(msg STRING)')
	deldb.commit()

def addtodb(msg):
	msgdb_cur.execute("INSERT INTO messages VALUES (?,?,?)", (msg.id, msg.date, msg._json))
	msgdb.commit()

def findbyid(msgid):
	msgdb_cur.execute('SELECT msg from messages WHERE id=%d'%msgid)
	msg=msgdb_cur.fetchone()[0]
	deldb_cur.execute("INSERT INTO messages VALUES (?)", (msg,))
	deldb.commit()
	msgdb_cur.execute('DELETE FROM messages WHERE id=%d'%msgid)
	msgdb.commit()
	print(json.loads(msg))

def mrproper():
	global mrproper_time
	if mrproper_time < 24*60**2:
		mrproper_time = time.time()
		cmd='DELETE FROM messages WHERE time < %d'%(int(time.time())-24*60**2)
		msgdb_cur.execute(cmd)
		msgdb.commit()
		print('mrproper: cleaning!')

vkbot = vk.vk(token=info.token)

def on_event(event):
	mrproper()
	if event[0] == 2:
		findbyid(event[1])
	elif event[0] == 4:
		msg=vkbot.messages.getById( message_ids=event[1]).response.items[0]
		addtodb(msg)

vkbot.lp_loop(on_event)
