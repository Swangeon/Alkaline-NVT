#!/usr/bin/env python3

from modules.comms import secure_send, recv_data, cget_pubkey
import nacl.utils
from nacl.public import PrivateKey, Box
import pickle
from shlex import split
import socket
from time import sleep

BUFFER_SIZE = 4096


class ClientService(object):
	def __init__(self, ip, port):
		# Setting up the client socket and keys
		self.conn_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.conn_object.connect((ip, port))
		except ConnectionRefusedError:
			print("[ERROR] Host is not online")
			exit()

		self.privkey = PrivateKey.generate()
		self.pubkey = self.privkey.public_key
		self.server_pubkey = cget_pubkey(self.conn_object, self.pubkey._public_key)

		self.client_box = Box(self.privkey, self.server_pubkey)


		self.client_handler()


	def output_data(self, response, cwd):
		"""
		Function to look at if the data is either pickled or just in normal utf-8 encoding
		"""
			#result = response.decode() # Normal utf-8 encoding
		if type(response) == str:
			print(response)

			return cwd
		else:
			# result = pickle.loads(response) # pickled encoding
			# When you change directories, the server sends back the 'Changed Direcotry' informationa and then the actual path
			print(response[0].decode())
			cwd = response[1].decode()
			return cwd

	def upload(self, upload_file):
		"""
		Function to upload a file to the server
		"""
		with open(upload_file, 'r') as file:
			# This will hold the text of the file
			file_buffer = file.readlines()

		file_name = upload_file.split('/')[-1]

		data = pickle.dumps(["upload", file_name, file_buffer])
		secure_send(self.conn_object, data, self.client_box)

	def download(self, data: list, filename: str):
		"""
		Function to download file from server
		"""
		with open(filename, 'w') as file:
			file.writelines(data)
			print(f"[SAVED] File {filename} Saved")


	def client_handler(self):
		try:
			try:
				# Getting cwd of server
				cwd = recv_data(self.conn_object, BUFFER_SIZE, self.client_box)
			except ConnectionResetError:
				print("[ERROR] Connection closed by server")
				exit(1)
			while True:
				# Get user input
				command = input(f"{cwd}> ")
				cmd_split = split(command)

				if not command:
					# Empty command
					continue

			# --------------------------------------------------------------------------------------------------------------------

				#If the user wants to upload call the upload function
				if cmd_split[0].lower() == "upload":
					try:
						file = self.upload(cmd_split[1])
					except (IndexError, FileNotFoundError):
						print("[ERROR] Please make sure you entered the path of the file right and/or that the file exists.")
						continue

				elif cmd_split[0].lower() == "download":
					if len(cmd_split) == 1:
						print("[ERROR] Please enter a file to download.")
						continue
					else:
						command = pickle.dumps(cmd_split)
						secure_send(self.conn_object, command, self.client_box)
				
				elif command.lower() == "exit":
					# Exit out of the current session
					break

				else:
					try:
						# Send clients command to server
						secure_send(self.conn_object, command.encode(), self.client_box)
					except BrokenPipeError:
						print("[ERROR] Server is offline")
						exit(1)


			# --------------------------------------------------------------------------------------------------------------------

				response = recv_data(self.conn_object, BUFFER_SIZE, self.client_box)
				
				if cmd_split[0] == "download":
					# For when we get a FileNotFound Error since the error is not sent through pickle serialization
						self.download(response, cmd_split[1].cmd_split('/')[-1])
				else:
					cwd = self.output_data(response, cwd)

		
		# Handle interrupt error
		except KeyboardInterrupt:
			print("\n[INFO] Closing connection and exiting client application...")
			secure_send(self.conn_object, b"exit", self.client_box)
			sleep(1)
			self.conn_object.close()

		else:
			# In case the user exits the application using the built in exit command
			secure_send(self.conn_object, b"exit", self.client_box)
			sleep(1)
			self.conn_object.close()