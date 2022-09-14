import socket
import sys
import select
import pdb
import util
from util import Hall,Room,Person

if len(sys.argv)>=2:
    host=sys.argv[1]
else:
    host=''

sock=util.create_socket((host,util.port))

hall =Hall()

conn_list=[]
conn_list.append(sock)

while True:
    read_persons, write_persons, error_sockets = select.select(conn_list, [], [])
    for person in read_persons:
        if person is sock:
            new_sock,addr =person.accept()
            new_person =Person(new_sock)
            conn_list.append(new_person)
            hall.new_person(new_person)
        else:
            message = person.socket.recv(4096)
            if message:
                message = message.decode().lower()
                hall.handle_msg(person,message)
            else:
                person.socket.close()
                conn_list.remove(person)
    for sock in error_sockets:
        sock.close()
        conn_list.remove(sock)

