#!/usr/bin/python

## This requires ICE to be enabled on murmur, and the Murmur Mice package
## http://wiki.mumble.info/wiki/Mice

## This check returns number of active connections, how many people are able to receive 
## a voice stream, how many are connected by deafened (could not receive voice), 
## and how many virtual servers are present.

import sys
import os
sys.path.append('/opt/murmur/ice')

sys.stdout = open(os.devnull, "w")
import mice
sys.stdout = sys.__stdout__

numberServers = len(mice.m.getAllServers())
usersOnline = 0
usersListening = 0
usersDeaf = 0

serverId = 1
#print "Getting stats for", numberServers,"servers"
for serverId in range(1, numberServers+1):
#       print "Getting stats for server", serverId
        server = mice.m.getServer(serverId)
#       print server
        users = server.getUsers()
#       print "Users online:", len(users), "List: ", users.keys()
        for user in users:
                usersOnline += 1
                if users[user].selfDeaf or users[user].deaf:
                        usersDeaf += 1
                else:
                        usersListening += 1

print "status ok"
print "metric servers int", numberServers, "servers"
print "metric online int", usersOnline,"users"
print "metric deaf int", usersDeaf,"users"
print "metric listening int", usersListening,"users"

