
import socket
import pdb


port = 9999
QUIT_STRING= '<#quit#>'


def create_socket(address):
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind(address)
    sock.listen(50)
    print("Listening at ",address)
    return sock


class Hall:
    def __init__(self):
        self.rooms = {} # {room_name: Room}
        self.room_person_map = {} # {playerName: roomName}

    def new_person(self, person):
        person.socket.sendall(b'Welcome!\nplease tell us your name: \n')
    
    def list_rooms(self,person):
        if len(self.rooms)==0:
            message = 'No active rooms present currently! Create your own group.\n' + 'Use [<join> room_name] to create a room.\n'
            person.socket.sendall(message.encode())
        else:
            message = 'Current rooms..\n'
            for room in self.rooms:
                message += room + ": " +str(len(self.rooms[room].persons)) + " person(s)\n"
            person.socket.sendall(message.encode())

    def handle_msg(self,person,msg):

        instructions = b'Instructions:\n'\
            + b'[<list>] to list all rooms\n'\
            + b'[<join> room_name] to join/create/switch to a room\n' \
            + b'[<manual>] to show instructions\n' \
            + b'[<quit>] to quit\n' \
            + b'Otherwise start typing and enjoy!' \
            + b'\n'

        print(person.name+" says "+msg)

        if "name: " in msg:
            name =msg.split()[1]
            person.name = name
            print("New connection from:",person.name)
            person.socket.sendall(instructions)
        
        elif "<join>" in msg:
            same_room =False
            if len(msg.split()) >= 2: # error check
                room_name = msg.split()[1]
                if person.name in self.room_person_map: # switching?
                    if self.room_person_map[person.name] == room_name:
                        person.socket.sendall(b'You are already in room: ' + room_name.encode())
                        same_room = True
                    else: # switch
                        old_room = self.room_person_map[person.name]
                        self.rooms[old_room].remove_person(person)
                if not same_room:
                    if not room_name in self.rooms: # new room:
                        new_room = Room(room_name)
                        self.rooms[room_name] = new_room
                    self.rooms[room_name].persons.append(person)
                    self.rooms[room_name].new_person(person)
                    self.room_person_map[person.name] = room_name
            else:
                person.socket.sendall(instructions)

        elif "<list>" in msg:
            self.list_rooms(person) 

        elif "<manual>" in msg:
            person.socket.sendall(instructions)
        
        elif "<quit>" in msg:
            person.socket.sendall(QUIT_STRING.encode())
            self.remove_person(person)

        else:
            if person.name in self.room_person_map:
                self.rooms[self.room_person_map[person.name]].broadcast_msg(person, msg.encode())
            else:
                msg = 'You are currently not in any room! \n' + 'Use [<list>] to see available rooms! \n' + 'Use [<join> room_name] to join a room! \n'
                person.socket.sendall(msg.encode())

    def remove_person(self,person):
        if person.name in self.room_person_map:
            self.rooms[self.room_person_map[person.name]].remove_person(person)
            del self.room_person_map[person.name]
        print(person.name +" has left\n")

            




class Room:
    def __init__(self, name):
        self.persons = [] 
        self.name = name
    
    def new_person(self, person):
        message = self.name +" "+ "welcomes " + person.name + "\n"
        for persons in self.persons:
            persons.socket.sendall(message.encode())

    def broadcast_msg(self, person, msg):
        message = person.name.encode() + b":"+msg
        for persons in self.persons:
            persons.socket.sendall(message)
    
    def remove_person(self,person):
        self.persons.remove(person)
        message = person.name.encode() + b"has left the room\n"
        self.broadcast_msg(person, message)


        

class Person:
    def __init__(self, socket , name ="new"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name

    def filenum(self):
        return self.socket.fileno()

        
