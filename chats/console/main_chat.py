from chats.console.base_chat import BaseChat, INDENT, BreakLoopException, lock
from chats.console.base_chat import print_information, parse_function
from chats.console.room_chat import RoomChat
from chats.console.user_chat import UserChat

import chats.console.base_chat as bc


class MainChat(BaseChat):
    def __init__(self, client):
        super().__init__(client)
        self.client = client
        self.commands = self.create_command_descrypt()

    def init_command_handlers(self):
        self.command_handlers = {
            '@help': self.print_help,
            '@users': self.print_users,
            '@rooms': self.print_rooms,
            '@exit': self.exit,
        }

    @print_information
    def print_users(self):
        for user_id in self.client.host2user_id.values():
            print('+ %s' % self.db_helper.get_username(user_id))

    @print_information
    def print_rooms(self):
        for room in self.db_helper.get_user_rooms():
            print('+ %s' % room)

    @parse_function
    def parse_user(self, parse):
        username = parse.group(1)
        if self.db_helper.user_exists(username):
            UserChat(username=username, client=self.client).open()
        else:
            print('[-] No such user in the chat\n')

    @parse_function
    def parse_room(self, parse):
        room_name = parse.group(1)
        if self.db_helper.room_exists(room_name):
            RoomChat(room_name=room_name, client=self.client).open()
        else:
            print('[-] No such room in the chat\n')

    @parse_function
    def parse_create_room(self, parse):
        room_name = parse.group(1)
        if self.db_helper.create_room(room_name):
            print('\n[+] You\'ve created room "{0}"\n'
                  .format(room_name))
        else:
            print('\n[-] Room with this name already exists\n')

    @parse_function
    def parse_username(self, parse):
        self.change_username(parse.group(1))


    @parse_function
    def parse_remove_room(self, parse):
        room_name = parse.group(1)
        self.remove_room(room_name)

    @parse_function
    def parse_add_user(self, parse):
        username = parse.group(1)
        room_name = parse.group(2)
        if not self.add_user2room(username, room_name):
            print('[-] Error while trying add user to the room')

    def run(self):
        if not self.cur_user_exists():
            self.specify_username()
        else:
            print('Hello again, %s!' % self.client.username)
        self.db_helper.specify_username(self.client)
        if not self.client.start():
            print('[-] Sorry. But it seems there isn\'t Internet connection')
            self.exit()
        self.command_mode()

    def create_command_descrypt(self):
        return {
            'help': 'Shows this output',
            'username "username"': 'Changes current username. ',
            'rooms': 'Shows available rooms.',
            'users': 'Shows online users.',
            'user "username"': 'Switches to user message mode. ',
            'room "room_name"': 'Switches to room message mode. ',
            'remove_room "roomname"': 'Removes created room.',
            'add_user': '"username" "room_name"',
            'create_room "roomname"': 'Creates new room. ',
            'exit': 'Closes chat.'
        }

    def handle_command(self, command):
        bc.operation_done = False
        user_parse = self.USER_PATTERN.match(command)
        room_parse = self.ROOM_PATTERN.match(command)
        username_parse = self.USERNAME_PATTERN.match(command)
        create_room_parse = self.CREATE_ROOM_PATTERN.match(command)
        remove_room_parse = self.REMOVE_ROOM_PATTERN.match(command)
        add_user_parse = self.ADD_USER_PATTERN.match(command)

        try:
            self.command_handlers[command]()
            bc.operation_done = True
        except KeyError:
            self.parse_user(user_parse)
            self.parse_room(room_parse)
            self.parse_username(username_parse)
            self.parse_create_room(create_room_parse)
            self.parse_remove_room(remove_room_parse)
            self.parse_add_user(add_user_parse)
        else:
            if not bc.operation_done:
                print('[-] Invalid command\n')

    def handle_signal(signal, frame):
        self.exit()

    def command_mode(self):
        print('\nType "@help" for list of commands with description')

        while True:
            try:
                command = input('[*] Enter command:> ')
                self.handle_command(command)
            except KeyboardInterrupt as e:
                self.exit()
