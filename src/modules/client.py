#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from nacl.public import PrivateKey, Box
import pickle
from modules.comms import secure_send, secure_recv, cget_pubkey
from shlex import split
from socket import socket, AF_INET, SOCK_STREAM


BUFFER_SIZE = 4096


class ClientSessionHandler(object):
    def __init__(self, ip: str, port: int, session: socket) -> None:
        """
        Initialization for the ClientSessionHandler.

        Args:
            ip (str): IP address of the server.
            port (int): Port of the server.

        Returns:
            None.
        """
        self.session = session
        self.private_key = PrivateKey.generate()
        self.public_key = self.private_key.public_key
        self.server_public_key = cget_pubkey(self.session, self.public_key._public_key)
        self.encryption_box = Box(self.private_key, self.server_public_key)

    def __output_data(self, response, cwd: str) -> str:
        """
        Output data that was sent from the server.

        Args:
            response: STDOUT of the command ran on the server.
            cwd: Current Working Directory.

        Returns:
            Return the current working directory of the server side.
        """
        if isinstance(response, str):
            print(response)
        else:
            # When you change directories, the server sends back the 'Changed Direcotry'
            # information and then the actual path
            print(response[0].decode())
            cwd = response[1].decode()
        return cwd

    def __upload(self, upload_file: str) -> None:
        """
        Uploads a file to the server.

        Args:
            upload_file (str): The path of the file to be uploaded.

        Returns:
            None.
        """
        with open(upload_file, 'r') as file:
            file_buffer = file.readlines()
        file_name = upload_file.split('/')[-1]
        data = pickle.dumps(["upload", file_name, file_buffer])
        secure_send(self.session, data, self.encryption_box)

    def __download(self, cmd_split: list[str]) -> None:
        """
        Downloads a file from the server.

        Args:
            cmd_split (list): Contains the command for the server to process.

        Returns:
            None.
        """
        if len(cmd_split) == 1:
            print("[ERROR] Please enter a file to download.")
        else:
            command = pickle.dumps(cmd_split)
            secure_send(self.session, command, self.encryption_box)
            response = secure_recv(self.session, BUFFER_SIZE, self.encryption_box)
            filename = cmd_split[1].split('/')[-1]
            with open(filename, 'w') as file:
                file.writelines(response)

    def client_handler(self) -> None:
        """
        Main method for handling the client session with the server.

        Args:
            None.

        Returns:
            None.
        """
        try:
            try:
                cwd = secure_recv(self.session, BUFFER_SIZE, self.encryption_box)
            except ConnectionRefusedError:
                print("[ERROR] Connection closed by server")
                return
            while True:
                command = input(f"{cwd}> ")
                cmd_split = split(command)
                if not command:
                    continue
                if cmd_split[0].lower() == "upload":
                    try:
                        self.__upload(cmd_split[1])
                    except (IndexError, FileNotFoundError):
                        print("[ERROR] Please make sure you entered the path of the file right \
                                and/or that the file exists.")
                    continue
                elif cmd_split[0].lower() == "download":
                    self.__download(cmd_split)
                elif command.lower() == "exit":
                    secure_send(self.session, b"exit", self.encryption_box)
                    self.session.close()
                    return
                else:
                    try:
                        # Default send client command to server
                        secure_send(self.session, command.encode(), self.encryption_box)
                    except BrokenPipeError:
                        print("[ERROR] Server is offline")
                        return
                if cmd_split[0] != "download":
                    response = secure_recv(self.session, BUFFER_SIZE, self.encryption_box)
                    cwd = self.__output_data(response, cwd)
        except KeyboardInterrupt:
            print("[INFO] Closing session and exiting client application...")
            secure_send(self.session, b"exit", self.encryption_box)
            self.session.close()
            return

    @classmethod
    def main_client(cls: object, ip_address: str, port: int) -> None:
        """
        Main method for creating the client session with the server.

        Args:
            cls (ClientSessionHandler): The ServerSessionHandler class.
            ip (str): IP address of the server.
            port (int): Port of the server.

        Returns:
            None.
        """
        session = socket(AF_INET, SOCK_STREAM)
        try:
            session.connect((ip_address, port))
        except ConnectionRefusedError as e:
            print(f"[ERROR] {e}: Host is not online")
        else:
            client = cls(ip_address, port, session)
            client.client_handler()
