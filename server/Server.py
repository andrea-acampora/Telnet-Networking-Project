#!/usr/bin/env python3
import socket, os, subprocess, sys

class Server:
    
    def __init__(self,ip,port):
        os.system("clear")
        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #aggiungo l'opzione che mi permette di riconnettermi e riutilizzare la connessione precedente.
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        server.bind((ip,port))
        server.listen(1)
        self.welcome_message = '\r\n[+]Authentication Completed! \r\n\nWelcome to Telnet Server !\r\n\r\nOptions:\r\n\r\n-> 1\tReturn the list of files in the directory\r\n-> 2\tReturn the path of the directory\r\n-> 3\tExecute a command on the Server shell\r\n-> 4\tChange directory\r\n-> 5\tRead the content of a Server file\r\n-> 6\tDownload a file from the Server\r\n-> 7\tUpload a file to the Server\r\n\n-> 0\tClose the connection\r\n'
        print("[+] Waiting for connections...")
        self.connection, address = server.accept()
        print("[+] New connection from: {}\n".format(str(address[0])))
    
    def authentication(self):
        print("[+] Starting Authentication :\n")
        self.send_to_client("[+] Enter the ip address [127.0.0.1]: ")
        self.client_ip = self.receive_from_client()
        self.send_to_client("[+] Enter the port [4444] : ")
        self.client_port = self.receive_from_client()
        if (self.client_ip == '127.0.0.1'  and self.client_port == '4444'):
            self.send_to_client("[+]Verificate")
            return True
        else:
            return False

    def send_to_client(self,data):
        self.connection.send(data.encode())
        
    def receive_from_client(self):
        return self.connection.recv(1024).decode()
    
    def send_file(self, path):
        with open(path, "r") as file:
            return str(file.read())
        
    def write_file(self, path, content):
        with open(path, "w") as file:
            file.write(content)
            return "[+] Uploaded --> " + path
        
    def execute_system_command(self,command):
        try:
            result = subprocess.run(command, capture_output=True)
            return str(result.stdout)
        except subprocess.CalledProcessError:
            return "[-] Error during command execution !"
        
    def change_dir(self, path):
        os.chdir(path)
        return "[+] Changed directory to " + path

    def run(self):
        if self.authentication():
            print("[+] Authentication Completed !\n")
            self.send_to_client(self.welcome_message)
            while True:
                recived_command = self.receive_from_client()
                try:
                    if recived_command == "0" or recived_command =="exit":
                        print("Quitting...")
                        os.system("clear")
                        self.connection.close()
                        sys.exit()
                    elif recived_command == "1":
                        command_result = '\r\n' + str(os.listdir()) + '\r'
                        print("[+] Sending the list of files in current directory")
                    elif recived_command == "2":
                        command_result = '\r\n'+str(os.getcwdb())+'\r'
                        print("[+] Sending the path of current directory")
                    elif recived_command =="3":
                        self.send_to_client("[+] Enter the command : ")
                        command_name = self.receive_from_client()
                        command_result = self.execute_system_command(command_name)
                        print("[+] Executing " + str(command_name))
                    elif recived_command == "4":
                        self.send_to_client("[+] Enter the name of the directory : ")
                        dir_name = self.receive_from_client()
                        command_result = self.change_dir(dir_name)
                        print(command_result)
                    elif recived_command in ["5","6"]:
                        self.send_to_client("[+] Enter the name of the file to read/download : ")
                        file_name = self.receive_from_client()
                        command_result = self.send_file(file_name)
                        print("[+] Sending {} to Client" .format(file_name))
                    elif recived_command =="7":
                        self.send_to_client("[+] Enter the name of the file to upload: ")
                        file_name = self.receive_from_client()
                        self.send_to_client("[+] Waiting for content of the file")
                        file_content = self.receive_from_client()
                        command_result = self.write_file(file_name, file_content)
                    else:
                        command_result = "\n[-] Error during command execution !"
                except Exception:
                        command_result = "\n[-] Error during command execution !"
                self.send_to_client(command_result)


server = Server("",4444)
server.run()  
    
    
        
    
        