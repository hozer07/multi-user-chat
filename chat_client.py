import json
from chatui import init_windows, read_command, print_message, end_windows
import threading
import sys
import socket

def construct_client_packet(packetType, payload=None):
    if("hello" == packetType):
        payload = {"type" : "hello", "nick" : payload}
    elif("chat" == packetType):
        payload = {"type" : "chat", "message" : payload}
    else:
        raise Exception
    json_data = json.dumps(payload)
    payloadLen = len(json_data)
    payloadLen = payloadLen.to_bytes(2, "big")
    payload = payloadLen + json_data.encode()
    return payload

def handle_server_packet(sock):
    codingFormat = "ISO-8859-1"
    receiveLength = 1024
    while True:
        receivedPacket = sock.recv(receiveLength)
        if( 0 == len(receivedPacket) ):
            raise Exception
        
        payloadLength = int.from_bytes(receivedPacket[:2], "big")
        if(0 >= payloadLength):
            raise Exception
        
        payload = receivedPacket[2 : 2 + payloadLength].decode()
        data = json.loads(payload)
        packetType = data["type"]
        if("chat" == packetType):
            print_message(data["nick"] + ": " + data["message"])
        elif("join" == packetType):
            print_message("*** " + data["nick"] + " has joined the chat" )
        elif("leave" == packetType):
            print_message("*** " + data["nick"] + " has left the chat" )
        else:
            raise Exception       
        

def main(argv):
    try:
        nick = argv[1]
        host = argv[2]
        port = int(argv[3])
    except:
        usage()
        return 1
    
    # Make the client socket and connect
    s = socket.socket()
    s.connect((host, port))
    
    # Start receiving thread
    t = threading.Thread(target=handle_server_packet, args=[s], daemon=True)
    t.start()
      
    init_windows()
    s.send(construct_client_packet("hello", nick))
    
    while True:
        try:
            message = read_command(nick + "> ")
            s.send(construct_client_packet("chat", message))
        except:
            break

    end_windows()
    t.join()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
