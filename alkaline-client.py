#!/usr/bin/env python3

"""
Author: Sean Brady
Date:03/10/2022

ATTENTION/CAUTION
I AM NOT RESPONSIBLE FOR ANY USER MISUSE OF THE CODE IN THIS REPOSITORY!
If you're using it as a reverse shell, only hack your own system/systems you have legal authority to use/pentest
"""

# Importing the modules I need
from argparse import ArgumentParser
from modules import logo, client_commands

if __name__ == '__main__':
	print(logo.logo)
	desc = """
	Alkaline: Interactive Network Client Bash Shell w/ Extra Commands:
	upload 'path-to-file-without-quotes' - Will upload a file from the client
	download 'path-to-file-without-quotes' - Will download a file from the server
	"""
	parser = ArgumentParser(description=desc,
		prog='alkaline-server.py',
		usage='python %(prog)s [options]')
	parser.add_argument("-a", "--ip-address", help="IP Address of Server to connect to.\nEX: 127.0.0.1", type=str, required=True)
	parser.add_argument("-p", "--port", help="Port of Server to connect to.\nEX: 5555", type=int, required=True)

	args = parser.parse_args()

	client_commands.ClientService(args.ip_address, args.port)


























