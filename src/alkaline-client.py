#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from argparse import ArgumentParser
from modules.client import ClientSessionHandler


with open('../logo.txt', 'r') as f:
    tmp = f.readlines()
    LOGO = r"".join(tmp)


if __name__ == '__main__':
    print(LOGO)
    desc = "Alkaline: Interactive Network Virtual Terminal"
    parser = ArgumentParser(description=desc,
                            prog='alkaline-server.py',
                            usage='python %(prog)s [options]')
    parser.add_argument("-a", "--ip-address", help="IP Address of Server to connect to.\nEX: \
                                            127.0.0.1", type=str, required=True)
    parser.add_argument("-p", "--port", help="Port of Server to connect to.\nEX: 5555",
                        type=int, required=True)
    args = parser.parse_args()
    ClientSessionHandler.main_client(args.ip_address, args.port)
    exit(0)
