import socket
import sys
import select
import util
from util import QUIT_STRING, Room,Person,Hall

if len(sys.argv) <2:
    print("Usage: python3 client.py [hostip] ",file=sys.stderr)
    sys.exit(1)
else:
    conn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    conn.connect((sys.argv[1], util.port))

print("Connected to Server\n")

def prompt():
    print('>', end=' ', flush = True)

sock_list=[sys.stdin,conn]
message_pre=""

while 1:
    read_persons,write_persons,error_sockets= select.select(sock_list, [], [])
  
    for sock in read_persons:
        if sock is conn:
            message=sock.recv(4096)
            if not message:
                print("Server Down!")
                sys.exit(2)
            else:
                if message==util.QUIT_STRING.encode():
                    sys.stdout.write("Bye\n")
                    sys.exit(2)
                else:
                    sys.stdout.write(message.decode())
                    if "please tell us your name" in message.decode():
                        message_pre="name: "
                    else:
                        message_pre=""
                    prompt()
        else:
            message=message_pre+sys.stdin.readline()
            conn.sendall(message.encode())
                    
