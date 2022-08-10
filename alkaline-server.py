#!/usr/bin/env python3

"""
Author: Sean Brady
Date:03/10/2022

ATTENTION/CAUTION
I AM NOT RESPONSIBLE FOR ANY USER MISUSE OF THE CODE IN THIS REPOSITORY!
If you're using it as a reverse shell, only hack your own system/systems you have legal authority to use/pentest
"""

# Importing the modules needed
from argparse import ArgumentParser
from modules.logo import logo
from modules.server_commands import Session_Handler
from multiprocessing import Process


import socket
import sys


def main_server(ip, port, output):
    """
    The main function to setup the server
    """

    if output == 0:
        sys.stdout = None

    print(logo)

    # Setting up the socket to use TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    # Telling the program that at the TCP layer, set reuse of local addresses to true
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #Binding the program to a IP and Port then listening for up to 5 connections
    sock.bind((ip, port))
    sock.listen(5)
    print(f"[INFO] Listening on port {port}")

    while True:
        try:
            # Waiting on the connection to come in and get a connection object to interact with our session 
            conn_object, address = sock.accept()
            client_ip = address[0]
            client_port = address[1]
            print(f"[INFO] Accepted connection from {client_ip}:{client_port}")

            # Initializing the session handler object 
            shell = Session_Handler(conn_object, client_ip, client_port)

            # Start a new process with each connection. We need new processes beacuse cd'ing can cause problems with all threads sharing the PID
            proc = Process(target=shell.session_handler)
            proc.start()


        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Shutting Servers Down...")
            sock.close()
            exit(1)





if __name__ == '__main__':
    desc = "Alkaline: Interactive Network Server Bash Shell"

    parser = ArgumentParser(description=desc,
        prog='alkaline-server.py',
        usage='python3 %(prog)s [options]')
    parser.add_argument("-a", "--ip-address", help="IP Address to Bind Server to.\nEX: 127.0.0.1", type=str, required=True)
    parser.add_argument("-p", "--port", help="Port to Bind Server to.\nEX: 5555", type=int, required=True)
    parser.add_argument("-o", "--output", help="Will set stdout for the program to be either 1 (The server can output to the console and is default) or 0 (The server will run in the background)", type=int, choices=[0, 1], default=1)

    args = parser.parse_args()

    main_server(args.ip_address, args.port, args.output)
