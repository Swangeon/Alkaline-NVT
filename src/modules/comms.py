#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from pickle import loads
import nacl.utils
import nacl.public
from socket import socket


PUBLIC_KEY_SIZE = 32


def sget_pubkey(session: socket, public_key: bytes) -> nacl.public.PublicKey:
    client_pubkey = session.recv(PUBLIC_KEY_SIZE)
    session.send(public_key)
    return nacl.public.PublicKey(client_pubkey)


def cget_pubkey(session: socket, public_key: bytes) -> nacl.public.PublicKey:
    session.send(public_key)
    server_pubkey = session.recv(PUBLIC_KEY_SIZE)
    print("[INFO] Obtained Server Public Key")
    return nacl.public.PublicKey(server_pubkey)


def secure_send(session: socket, data_to_send: bytes, box_of_host: nacl.public.Box) -> None:
    data = box_of_host.encrypt(data_to_send)
    session.send(data)


def secure_recv(session: socket, buffer: int, box: nacl.public.Box):
    data = b""
    data += session.recv(buffer)
    # looping until said data is done sending since we may have to fragment the data
    try:
        session.settimeout(.1)
        while True:
            try:
                data += session.recv(buffer)
            except TimeoutError:
                break
        session.settimeout(None)
    except KeyboardInterrupt:
        exit(1)
    return __decrypt_data(data, box)


def __decrypt_data(encrypted_data: bytes, box: nacl.public.Box):
    """
    Private function to decrypt the data
    """
    decrypted_data = box.decrypt(encrypted_data)
    try:
        output = decrypted_data.decode()
    except UnicodeDecodeError:
        return loads(decrypted_data)
    return output
