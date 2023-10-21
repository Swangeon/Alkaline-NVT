#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Sean Brady
Date: 09/23/2023
"""


from argparse import ArgumentParser
from modules.server import ServerSessionHandler


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
    ServerSessionHandler.main_server(args.address, args.port, args.debug)
    exit(0)
