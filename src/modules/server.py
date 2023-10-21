#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
from modules.comms import secure_send, secure_recv, sget_pubkey
from multiprocessing import Process
from nacl.public import PrivateKey, Box
import pickle
import os
import shlex
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import subprocess


BUFFER_SIZE = 4096 * 256


class ServerSessionHandler(object):
    def __init__(self, conn: socket, ip: str, port: int, debug: int) -> None:
        """
        Initialization for the ServerSessionHandler.

        Args:
            conn (socket): socket object
            ip (str): IP address of the server
            port (int): port of the server
            debug (int): debug level

        Returns:
            None.
        """
        if debug == 1:
            logging.basicConfig(level=logging.DEBUG)
        self.session = conn
        self.ip = ip
        self.port = port
        self.private_key = PrivateKey.generate()
        self.public_key = self.private_key.public_key
        self.client_public_key = sget_pubkey(self.session, self.public_key._public_key)
        self.encryption_box = Box(self.private_key, self.client_public_key)

    def send_cwd(self) -> None:
        """
        Sends the current working directory to the client.

        Args:
            None.

        Returns:
            None.
        """
        try:
            cwd = f"\r{os.getcwd()}".encode()
            secure_send(self.session, cwd, self.encryption_box)
        except BrokenPipeError:
            logging.debug(f"[INFO] USER {self.ip}:{self.port} DISCONECTED")

    def change_directory(self, cmd_split: list[str]) -> bytes:
        """
        Handles the `cd` command to change the working directory.

        Args:
            cmd_split (list): Contains the command from the client.

        Returns:
            The output needed for the client to recognize the server changing the
            working directory.
        """
        output = b""
        try:
            os.chdir(''.join(cmd_split[1]))
        except FileNotFoundError as e:
            output = f"[ERROR] {e}".encode()
        cwd = os.getcwd().encode()
        array = pickle.dumps([output, cwd])
        return array

    def execute(self, cmd_split: list[str]) -> bytes:
        """
        Executes the command recieved from the client.

        Args:
            cmd_split (list): Contains the command from the client.

        Returns:
            The output needed for the client to recognize the command being processed.
        """
        try:
            output = subprocess.check_output(cmd_split, stderr=subprocess.STDOUT)
            return output
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            output = f"[ERROR] {e}".encode()
            return output

    def __upload_write_file(self, cmd_split: list[str]) -> None:
        """
        Writes the file to disk that the client is trying to upload.

        Args:
            cmd_split (list): Contains the name (at index 0) and content (at index 1)
            of the file.

        Returns:
            None.
        """
        with open(cmd_split[1], "w") as file:
            file.writelines(cmd_split[2])
        logging.debug(f"[SAVED] File {cmd_split[1]} Saved")

    def __download(self, cmd_split: list[str]) -> bytes:
        """
        Retrieves the contents of a file from the server's filesystem.

        Args:
            cmd_split (list): Contains the name of the file at index 1.

        Returns:
            Contents of the file in byte.
        """
        file_buffer = ""
        try:
            with open(cmd_split[1], "r") as file:
                file_buffer = "".join(file.readlines())
            return file_buffer.encode()
        except FileNotFoundError:
            return b"[ERROR] File not found, please enter the correct path and/or make sure that \
                the file exists on the system."

    def server_handler(self) -> None:
        """
        Main method for handling the server session with the client.

        Args:
            None.

        Returns:
            None.
        """
        self.send_cwd()
        try:
            while True:
                output = b''
                cmd = secure_recv(self.session, BUFFER_SIZE, self.encryption_box)
                if not cmd:
                    continue
                logging.debug(f"[COMMAND INFO] Received: {cmd}")
                if isinstance(cmd, str):
                    # The data that comes in needs to be split due to how subprocess.check_output
                    # works
                    splited_cmd = shlex.split(cmd)
                    if cmd.lower() == "exit":
                        logging.debug(f"[INFO] USER {self.ip}:{self.port} DISCONECTED")
                        return
                    elif splited_cmd[0].lower() == "cd":
                        output = self.change_directory(splited_cmd)
                    else:
                        output = self.execute(splited_cmd)
                else:
                    if cmd[0].lower() == "upload":
                        self.__upload_write_file(cmd)
                        continue
                    else:
                        output = self.__download(cmd)
                if output:
                    try:
                        secure_send(self.session, output, self.encryption_box)
                    except BrokenPipeError:
                        # If the user is disconnected randomly then stop this connection
                        logging.debug(f"[INFO] USER {self.ip}:{self.port} DISCONECTED")
                        exit(1)
                else:
                    secure_send(self.session, b"[INFO] Command executed", self.encryption_box)
        except Exception as e:
            logging.debug(f"[SHUTDOWN] Closing Sever due to Error: {e}")
            self.session.close()

    @classmethod
    def main_server(cls: object, ip: str, port: int, debug: int) -> None:
        """
        Main method for creating the server session with the client.

        Args:
            cls (ServerSessionHandler): The ServerSessionHandler class.
            ip (str): IP address of the server.
            port (int): Port of the server.
            debug (int): Debug mode switch.

        Returns:
            None.
        """
        if debug == 1:
            logging.basicConfig(level=logging.DEBUG)
        sock = socket(AF_INET, SOCK_STREAM)
        # Telling the program that at the TCP layer, set reuse of local addresses to true
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((ip, port))
        sock.listen(10)
        logging.debug(f"[INFO] Listening on {ip}:{port}")
        while True:
            try:
                try:
                    conn_object, address = sock.accept()
                except KeyboardInterrupt:
                    logging.debug("\r[SHUTDOWN] Shutting Servers Down...")
                    sock.close()
                client_ip = address[0]
                client_port = address[1]
                logging.debug(f"[INFO] Accepted connection from {client_ip}:{client_port}")
                terminal = cls(conn_object, client_ip, client_port, debug)
                # Start a new process with each connection since we can use cd and while
                # threading it can cause problems with all threads sharing the PID
                proc = Process(target=terminal.server_handler)
                proc.start()
            except KeyboardInterrupt:
                logging.debug("\r[SHUTDOWN] Shutting Servers Down...")
                sock.close()
