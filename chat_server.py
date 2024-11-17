# Example usage:
#
# python select_server.py 3490

import sys
import socket
import select
import json

def create_server_packet(packetType, nick, payload=None):
    if("chat" == packetType):
        payload = {"type" : "chat", "nick" : nick, "message" : payload}
    elif("join" == packetType):
        payload = {"type" : "join", "nick" : nick}
    elif("leave" == packetType):
        payload = {"type" : "leave", "nick" : nick}
    else:
        raise Exception
    json_data = json.dumps(payload)
    payloadLen = len(json_data)
    payloadLen = payloadLen.to_bytes(2, "big")
    payload = payloadLen + json_data.encode()
    return payload


def handle_client_packet(clientSocket, sockets, usersOfSockets):
    codingFormat = "ISO-8859-1"
    receiveLength = 1024
    receivedPacket = clientSocket.recv(receiveLength)
    if(0 == len(receivedPacket)):
        sockets.remove(clientSocket)
        nick = usersOfSockets[clientSocket]
        del usersOfSockets[clientSocket]     
        return create_server_packet("leave", nick)
    
    payloadLength = int.from_bytes(receivedPacket[:2], "big")
    if(0 >= payloadLength):
        raise Exception
    
    payload = receivedPacket[2 : 2 + payloadLength].decode()
    data = json.loads(payload)
    if("hello" == data["type"]):
        usersOfSockets[clientSocket] = data["nick"]
        return create_server_packet("join", data["nick"])
    elif("chat" == data["type"]):
        return create_server_packet("chat", usersOfSockets[clientSocket], data["message"])
    else:
        raise Exception
    
    

def run_server(port):
    messageDelimiter = "\n"
    mainSocket = socket.socket()
    mainSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mainSocket.bind(('',port))
    mainSocket.listen()
    sockets = {mainSocket}
    usersOfSockets = dict()
    while True:
        readSockets, _, _ = select.select(sockets, {}, {})
        for oneSocket in readSockets:
            if(oneSocket == mainSocket):
                newConn = mainSocket.accept()
                newSocket = newConn[0]
                sockets.add(newSocket)
            else:
                serverPacket = handle_client_packet(oneSocket, sockets, usersOfSockets)
                for sock in sockets:
                    if(sock == mainSocket):
                        continue
                    sock.send(serverPacket)
                

#--------------------------------#
# Do not modify below this line! #
#--------------------------------#

def usage():
    print("usage: chat_server.py port", file=sys.stderr)

def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    run_server(port)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
