from pickle import loads
import nacl.utils
from nacl.public import PrivateKey, Box
import socket


def sget_pubkey(conn_object: socket.socket, public_key: bytes) -> bytes:
	"""
	Function for server to get clients public key
	"""

	client_pubkey = conn_object.recv(32)
	conn_object.send(public_key)

	print("[INFO] Obtained Clients Public Key")
	return nacl.public.PublicKey(client_pubkey)

def cget_pubkey(conn_object: socket.socket, public_key: bytes) -> bytes:
    """
	Function for client to get servers public key
    """

    conn_object.send(public_key)
    server_pubkey = conn_object.recv(32)

    print("[INFO] Obtained Server Public Key")
    return nacl.public.PublicKey(server_pubkey)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def secure_send(conn_object: socket.socket, data_to_send, box_of_host: bytes):
	"""
	Send/stream the encrypted data  
	"""
	data = box_of_host.encrypt(data_to_send)
	conn_object.send(data)
	

def recv_data(conn_object: socket.socket, buffer: int, box: bytes):
	"""
	Revieve the servers output of command
	Thinking about making this asyncronous later
	"""
	data = b""
	data += conn_object.recv(buffer)
	# looping until said data is done sending since we have to fragment the data due to RSA
	while True:
		try:
			conn_object.settimeout(.1)
			data += conn_object.recv(buffer)
		except socket.timeout:
			conn_object.settimeout(None)
			break

	return __decrypt_data(data, box)
		

def __decrypt_data(enc_data: bytes, box: bytes):
	output = box.decrypt(enc_data)
	try:
		output = output.decode()
	except UnicodeDecodeError:
		return loads(output)

	return output