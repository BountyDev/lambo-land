import asyncore
import socket
from packet import Packet
from match import Match
from utils import Utils
from pregame import preGame
import threading
import random
import time
import struct
import json

def server(port):
    random.seed(time.time())
    outgoing = []
    BS = 10024
    ids = {}
    total = 0
    conns = {}
    total = {}
    users = {}
    active_players = {}
    queue = []
    arr = {}
    games = {}
    un = {}
    wpon = []
    matches = {}
    utils = Utils()

    #Constants
    BIT = 0
    BYTE = 1
    STRING = 2
    INT = 3
    DOUBLE = 4
    FLOAT = 5
    SHORT = 6
    USHORT = 7
    def readstring(mess):
        global mes
        s=""
        p=""
        while(p!="\x00"):
            p=struct.unpack('s', mess[:1])[0].decode("utf-8")
            mess=mess[1:]
            s+=p
        mes = mess
        return s[:-1]

    def readint(mess):
        global mes
        old = mess
        mes = mess[4:]
        return struct.unpack('i', old[:4])[0]

    def rec(message):
      global mes
      mes = message
      packet = Packet()
      arr[0] = readstring(mes)

      if arr[0] == 'register':
            username = readstring(mes)
            password = utils.hash_password(readstring(mes))
            id = readint(mes)
            with open("users.json") as f:
                data = json.load(f)
            if username not in data:
                data[username] = password
                print(f"{username} has registed")
            with open("users.json", 'w+') as f:
                json.dump(data, f)
            remove = []
            i = ids[id]
            try:
                packet.clear()
                packet.write(2, 'register')
                packet.write(2, "success")
                packet.send(i, packet)
            except Exception:
                remove.append(i)

      if arr[0] == 'create':
          pid = readint(mes)
          title = readstring(mes)

          matches[len(matches)] = preGame(pid, len(matches), title)

          send = ids[pid]

          packet.clear()
          packet.write(2, 'create')
          packet.send(send, packet)

      if arr[0] == 'login':
            vers = readint(mes)
            username = readstring(mes)
            password = readstring(mes)
            id = readint(mes)
            with open("users.json") as f:
                data = json.load(f)
            #with open("discord.json") as f:
            #    disc = json.load(f)
            #if "online" not in disc:
            #    disc["online"] = 0
            if username in data:
                if utils.verify_password(data[username], password):
                    if vers == 1:
                        if username not in active_players:
                        #    disc["online"]+=1
                            users[id] = username
                            active_players[username] = True
                            print(f"{username} has logined")
                            remove = []

                            update = ['login data', "success"]
                            i = ids[id]
                            try:
                                packet.clear()
                                packet.write(2, 'login')
                                packet.write(2, "success")
                                packet.write(3, id)
                                packet.send(i, packet)
                            except Exception:
                                remove.append(i)
                        else:
                            print("Played already logined")
                            active_players.pop(username)
                with open("users.json", 'w+') as f:
                    json.dump(data, f)


      if arr[0] == "queue":
          pid = readint(mes)
          weapon = readstring(mes)
          queue.append(pid)
          wpon.append(weapon)
          print("Entered Queue")

          if len(queue) == 2:
              print("Match found")
              new = {}
              random.seed(time.time())
              map = random.randint(0,2)
              rule = random.randint(0,2)
              num = 0
              for i in queue:
                new[num] = i
                packet.clear()
                packet.write(2, 'queue')
                packet.write(3, len(games))
                packet.write(3, num)
                packet.write(3, map)
                packet.write(3, rule)
                for l in wpon:
                    packet.write(2, l)
                packet.send(ids[i], packet)
                num+=1
              queue.clear()
              games["game" + str(len(games))] = Match(new[0], new[1], ids[new[0]], ids[new[1]],weapon, weapon)


      if arr[0] == "ping":
          pid = readint(mes)
          tm = readint(mes)
          if pid in ids:
              packet.clear()
              packet.write(2,"ping")
              packet.write(3, tm)
              packet.write(3, len(ids))
              packet.send(ids[pid], packet)

      if arr[0] == "leave":
          pid = readint(mes)
          if pid in queue:
              queue.remove(pid)

      if arr[0] == "join":
          gn = readint(mes)
          user = readstring(mes)
          pid = readint(mes)

          matches[gn].join(user)

      if arr[0] == "list":
          pid = readint(mes)
          send = []
          for i in matches:
              send.append(matches[i].list())
          packet.clear()
          packet.write(2, "list")
          packet.write(3, len(send))
          for i in send:
              packet.write(2, i[0])
              packet.write(3, i[1])
          packet.send(ids[pid], packet)


      if arr[0] == "move":
          xx = readint(mes)
          yy = readint(mes)
          pid = readint(mes)
          match = readint(mes)
          pn = readint(mes)
          #xs = readint(mes)
          if "game"+str(match) in games:
              cur = games["game" + str(match)]
              cur.update(xx,yy,pn)

              send = cur.grab(pn)

              packet.clear()
              packet.write(2, 'move')
              packet.write(3, xx)
              packet.write(3, yy)
              packet.send(send, packet)

      if arr[0] == "end":
          game = readint(mes)

          if "game" + str(game) in games:
              cur = games["game" + str(game)]

              players = cur.list()

              for i in players:
                  packet.clear()
                  packet.write(2, 'end')
                  packet.send(i, packet)
              games.pop("game"+str(game))

      if packet.Buffer > 0:
          rec(mes)

    class MainServer(asyncore.dispatcher):
      def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('127.0.0.1', port))
        self.listen(50)
        print("Server is up")
      def handle_accept(self):
        conn, addr = self.accept()
        print ('Connection address:' + addr[0] + " " + str(addr[1]))
        conn.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

        newid = random.randint(1,99999)
        while newid in un:
            newid = random.randint(1,99999)
        playerid = newid
        conns[conn] = playerid
        update = ['id update', playerid]
        ids[playerid] = conn
        username = 'user' + str(random.randint(1,999))
        un[playerid] = username
        packet = Packet()
        packet.clear()
        packet.write(2, 'init')
        packet.write(2, username)
        packet.write(3, playerid)
        packet.send(conn, packet)
        Run(conn, playerid)

    class Run(asyncore.dispatcher_with_send):
      def __init__(self, cd, pi):
          self.pi = pi
          threading.Thread.__init__(self)
          asyncore.dispatcher_with_send.__init__(self, cd)

      def handle_read(self):
        recievedData = self.recv(BS)
        if recievedData:
          rec(recievedData)
        else:
            player_id = self.pi
            ids.pop(player_id)
            un.pop(player_id)

            users.pop(player_id)
            if player_id in active_players:
                active_players.pop(users[player_id])

            if player_id in queue:
                queue.remove(player_id)
            num = ""
            for i in matches:
                check = matches[i].leave(player_id)

                if check != False:
                    matches.pop(i)
                    for i in check:
                        packet = Packet()
                        packet.clear()
                        packet.write(2, 'leave')
                        packet.send(ids[i], packet)

            self.close()


    MainServer(port)
    asyncore.loop()

server(4000)
