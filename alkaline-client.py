#!/usr/bin/env python3
"""
Author: Sean Brady
Date: 09/23/2023
"""


from argparse import ArgumentParser
from modules.logo import logo
from modules.client import ClientSessionHandler
from socket import socket, AF_INET, SOCK_STREAM


def main_client(ip_address: str, port: int):
	session = socket(AF_INET, SOCK_STREAM)
	try:
		session.connect((ip_address, port))
	except ConnectionRefusedError as e:
		print(f"[ERROR] {e}: Host is not online")
	else:
		session = ClientSessionHandler(ip_address, port, session)
		session.client_handler()

if __name__ == '__main__':
	print(logo)
	desc = "Alkaline: Interactive Network Virtual Terminal"
	parser = ArgumentParser(description=desc,
		prog='alkaline-server.py',
		usage='python %(prog)s [options]')
	parser.add_argument("-a", "--ip-address", help="IP Address of Server to connect to.\nEX: \
					 127.0.0.1", type=str, required=True)
	parser.add_argument("-p", "--port", help="Port of Server to connect to.\nEX: 5555", 
					type=int, required=True)
	args = parser.parse_args()
	main_client(args.ip_address, args.port)
	



























