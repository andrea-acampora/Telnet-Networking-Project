#!/usr/bin/env python3
import socket, os, subprocess, sys, json, ast

class Server:
    
    def __init__(self,ip,port):
        self.clearShell()
        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #aggiungo l'opzione che mi permette di riconnettermi e riutilizzare la connessione precedente.
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        server.bind((ip,port))
        server.listen(1)
        self.credentialsFile = os.path.expanduser('~/.credentials.txt')
        self.initCredentials(self.credentialsFile)
        self.welcome_message = '\nWelcome to Telnet Server !\r\n\r\nOptions:\r\n\r\n-> 1\tReturn the list of files in the directory\r\n-> 2\tReturn the path of the directory\r\n-> 3\tExecute a command on the Server shell and get the output\r\n-> 4\tChange directory\r\n-> 5\tRead the content of a Server file\r\n-> 6\tDownload a file from the Server\r\n-> 7\tUpload a file to the Server\r\n\n-> 0\tClose the connection\r\n'
        print("[+] Waiting for connections...")
        self.connection, address = server.accept()
        print("[+] New connection from: {}\n".format(str(address[0])))
    
    def authentication(self):
        print("[+] Starting Authentication....\n")
        self.send_to_client("[+] Enter the username : ")
        username = self.receive_from_client()
        self.send_to_client("[+] Enter the password : ")
        pwd = self.receive_from_client()
        if (username in self.credentials.keys() and self.credentials[username] == pwd):
            self.send_to_client("[+] Verificate")
            print("[+] Authentication Completed !\n")
        else:
            self.send_to_client("[-] Authentication failed!")
            print("[-] Authentication Failed for user : {} \n".format(username))
            self.send_to_client("\n[-] Authentication Failed !\n[+] Do you want to continue ad register it? [y/n] : ")
            answer = self.receive_from_client()
            if answer !="n":
                self.credentials[username] = pwd
                self.writeCredentialsOnFile(self.credentials)
                print("[+] Authentication Completed -> new user {} registered ! ".format(username))
            else:
                print("\n[-] Quitting....\n")
                self.connection.close()
                sys.exit()        

    def getCredentials_from_file(self):
        with open(self.credentialsFile,'r') as file:
            return ast.literal_eval(file.read())

    def initCredentials(self, filePath):
        if not os.path.exists(self.credentialsFile):
            startingAccounts = {'admin' : 'admin', 'andrea' : 'prova123'}
            self.writeCredentialsOnFile(startingAccounts)
        self.credentials = self.getCredentials_from_file()
        
    def writeCredentialsOnFile(self, credentials):
        with open(self.credentialsFile,'w') as file:
            file.write(str(credentials))
        
    def send_to_client(self,data):
        self.connection.send(json.dumps(data).encode())
        
    def receive_from_client(self):
        json_data = ""
        while True:
            try:
                json_data = json_data +self.connection.recv(1024).decode()
                return json.loads(json_data)
            except ValueError:
                continue
    
    def send_file(self, path):
        try:
            with open(path, "r") as file:
                return str(file.read())
        except FileNotFoundError:
            return "[-] File Not Found !"
        
        
    def write_file(self, path, content):
        with open(path, "w") as file:
            file.write(content)
            return "[+] Uploaded --> " + path
        
    def execute_system_command(self,command):
        try:
            command = command.split(" ")
            result = subprocess.run(command, capture_output=True)
            return str(result.stdout)
        except FileNotFoundError:
            return "[-] Error in command execution on Server !"
    
    def clearShell(self):
        os.system('cls||clear')
    
    def change_dir(self, path):
        os.chdir(path)
        return "[+] Changed directory to " + path

    def run(self):
        self.authentication()
        self.send_to_client(self.welcome_message)
        while True:
            recived_command = self.receive_from_client()
            try:
                if recived_command == "0" or recived_command =="exit":
                    print("\n[-] Quitting....\n")
                    self.connection.close()
                    sys.exit()
                elif "h" in recived_command:
                    command_result = self.welcome_message
                elif recived_command == "1":
                    command_result = '\r\n' + str(os.listdir()) + '\r'
                    print("[+] Sending the list of files in current directory\n")
                elif recived_command == "2":
                    command_result = '\r\n'+str(os.getcwdb())+'\r'
                    print("[+] Sending the path of current directory\n")
                elif recived_command =="3":
                    self.send_to_client("[+] Enter the command : ")
                    command_name = self.receive_from_client()
                    command_result = self.execute_system_command(command_name)
                    print("[+] Executing command -> {} \n".format(command_name))
                elif recived_command == "4":
                    self.send_to_client("[+] Enter the name of the directory : ")
                    dir_name = self.receive_from_client()
                    command_result = self.change_dir(dir_name)
                    print(command_result)
                elif recived_command in ["5","6"]:
                    self.send_to_client("[+] Enter the name of the file : ")
                    file_name = self.receive_from_client()
                    command_result = self.send_file(file_name)
                    if not "[-]" in command_result:
                        print("[+] Sending {} to Client\n" .format(file_name))
                    else :
                        print("[-] Failed to send {} : File Not Found ! \n".format(file_name))
                elif recived_command =="7":
                    self.send_to_client("[+] Enter the name of the file to upload: ")
                    file_name = self.receive_from_client()
                    self.send_to_client("[+] Waiting for content of the file")
                    file_content = self.receive_from_client()
                    if not "[-]" in file_content:
                        command_result = self.write_file(file_name, file_content)
                    else :
                        command_result = "[-] Failed to upload -> {} : File Not Found !\n".format(file_name)
                    print(command_result)
                else:
                    command_result = "[-] Command not found !\n"
            except Exception:
                    command_result = "\n[-] Error in command execution !\n"
            self.send_to_client(command_result)

server = Server("",4444)
server.run()  