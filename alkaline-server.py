#!/usr/bin/env python3
"""
Author: Sean Brady
Date: 09/23/2023
"""


from argparse import ArgumentParser
import logging
from modules.logo import logo
from modules.server import ServerSessionHandler
from multiprocessing import Process
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR


def main_server(ip, port, debug):
	if debug == 1:
		logging.basicConfig(level=logging.DEBUG)
	logging.debug(logo)
	sock = socket(AF_INET, SOCK_STREAM)
	# Telling the program that at the TCP layer, set reuse of local addresses to true
	sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	sock.bind((ip, port))
	sock.listen(10)
	logging.debug(f"[INFO] Listening on {ip}:{port}")
	while True:
		try:
			conn_object, address = sock.accept()
			client_ip = address[0]
			client_port = address[1]
			logging.debug(f"[INFO] Accepted connection from {client_ip}:{client_port}")
			shell = ServerSessionHandler(conn_object, client_ip, client_port, debug)
			# Start a new process with each connection. We need new processes beacuse cd'ing
			# while threading can cause problems with all threads sharing the PID
			proc = Process(target=shell.server_handler)
			proc.start()
		except KeyboardInterrupt:
			logging.debug("\r[SHUTDOWN] Shutting Servers Down...")
			sock.close()
			exit(1)


if __name__ == '__main__':
	desc = "Alkaline: Interactive Network Virtual Terminal"
	parser = ArgumentParser(description=desc,
		prog='alkaline-server.py',
		usage='python3 %(prog)s [options]')
	parser.add_argument("-a", "--address", help="IP Address to Bind Server to.\nEX: 127.0.0.1",
						type=str, required=True)
	parser.add_argument("-p", "--port", help="Port to Bind Server to.\nEX: 5555",
						type=int, required=True)
	parser.add_argument("-d", "--debug", help="Toggle Debug Mode. 0 for False (default), 1 for \
						True", type=int, choices=[0, 1], default=0)
	args = parser.parse_args()
	main_server(args.address, args.port, args.debug)
