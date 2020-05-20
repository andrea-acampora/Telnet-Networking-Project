#!/usr/bin/env python3
import socket, subprocess, argparse , os , sys, json, base64

class Client:
	def __init__(self):
		self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		option = self.get_arguments()
		self.connection.connect((option.server_ip, 4444))
		self.clearShell()

	def get_arguments(self):
		parser = argparse.ArgumentParser()
		parser.add_argument("-ip","--address",dest="server_ip", help="[+] Insert the Server IP Address")
		option = parser.parse_args()
		if not option.server_ip:
			option.server_ip= '127.0.0.1'
		return option	
	
	def authenticate(self):
		print("[+] Authentication :\n")
		request = self.receive_from_server()
		result = input(request)
		self.send_to_server(result)
		request = self.receive_from_server()
		result = input(request)
		self.send_to_server(result)
		auth_response = self.receive_from_server()
		if not "[+]" in auth_response:
			registration_confirm = input(self.receive_from_server())
			self.send_to_server(registration_confirm)
			if registration_confirm == "n" or registration_confirm =="N" or registration_confirm =="no":
				print("\n [-] Quitting....\n")
				self.connection.close()
				sys.exit()

	def send_to_server(self, data):
		self.connection.send(json.dumps(data).encode())

	def receive_from_server(self):
		json_data = ""
		while True:
			try:
				json_data = json_data +self.connection.recv(1024).decode()
				return json.loads(json_data)
			except ValueError:
				continue

	def download_file(self, path, content):
		with open(path,"w") as file:
			file.write(content)
			return "[+] File {}  succesfully downloaded !".format(path)

        
	def upload_file(self, path):
		with open(path, "r") as file:
			return str(file.read())	

	def clearShell(self):
		os.system('cls||clear')
        
	def execute_on_server(self, command):
		self.send_to_server(command)
		if command=="exit" or command=="0":
			print("\n[-] Quitting....\n")
			self.connection.close()
			exit()
		return self.receive_from_server()

	def run(self):
		self.authenticate()
		print(self.receive_from_server())
		while True:
			command = input("\nEnter [0-7] or [help] -> ")
			try:
				result = self.execute_on_server(command)
				if command in ["3","4","5","6","7"]:
					new_command = input(result)
					result = self.execute_on_server(new_command)
					if command =="7":
						file_content = self.upload_file(new_command)
						if (file_content):
							self.send_to_server(file_content)
							result = self.receive_from_server()
						else:
							result = "[-] File not found !"
					if command == "6":
						result = self.download_file(new_command, result)
			except Exception:
				result = "[-] Error in command execution "
			print(result)
				
try:
	client = Client()
	client.run()
except Exception: #per non mostrare messagio di errore se non ce un server
    client.clearShell()
    print("[-] Error: No Server found!")
    sys.exit()