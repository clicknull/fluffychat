import threading

from chats.console.base_chat import BaseChat, INDENT, BreakLoopException, lock
from chats.console.base_chat import print_information

from opt.appearance import cprint


class UserChat(BaseChat):
    def __init__(self, username, client):
        super().__init__(client)
        self.init_command_handlers()

        self.username = username
        self.user_id = self.db_helper.get_user_id(username)

        if self.user_id == self.client.user_id:
            self.self_chat = True

        self.print_mode_help('message')
        self.init_print_messages()

    def handle_command(self, command):
        send_file_parse = self.SEND_FILE_PATTERN.match(command)

        try:
            self.command_handlers[command]()
            bc.operation_done = True
        except KeyError:
            if send_file_parse:
                self.parse_sending_file(send_file_parse,
                                        username=self.username)
            else:
                if not self.send_message(username=self.username, text=command):
                    cprint('<lred>[-]</lred> Error occured while '
                           'message is sending')

    def open(self):
        self.print_last_messages(self.user_id)

        while True:
            try:
                try:
                    input()
                    with lock:
                        message = self.user_input()
                    self.handle_command(message)
                except KeyboardInterrupt:
                    self.back2main()
            except BreakLoopException:
                self.self_chat = False
                break

    def create_command_descrypt(self):
        return {
            'help': 'Shows this output',
            'back': 'Returns to message mode',
            'send_file "file location"': 'Sends file to an user'
        }
