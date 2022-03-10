##############################################################################
# server.py
##############################################################################
import ast
import random
import socket
import select
import chatlib_skeleton
import requests
import json
import html


# Data Loaders #

def load_questions_from_web ():
	url = requests.get("https://opentdb.com/api.php?amount=50")
	dict_ques = url.json()
	questions = { }

	for index, question in enumerate( dict_ques["results"]):
		t =[html.unescape(i) for i in question['incorrect_answers'] ]
		t.append(html.unescape(question['correct_answer']))
		t.sort()
		questions[index+1] = {"question" : html.unescape(question['question']), "answers" : t , "correct" : html.unescape(question['correct_answer'])}
	return questions


def load_user_database():
	f = open("C:\\Users\menyb\PycharmProjects\\NetWork.py\Trivia\\u1\\users.txt", "r")
	users = f.read()
	users_dict = ast.literal_eval(users)
	f.close()
	return users_dict


# GLOBALS
users = load_user_database()
questions = load_questions_from_web()
logged_users = {} # a dictionary of client hostnames to usernames - will be used later

messages_to_send = []

client_sockets = []

ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS

def build_and_send_message(conn, code, msg):
	## copy from client

	global messages_to_send
	full_msg = chatlib_skeleton.build_message(code, msg)
	messages_to_send.append((conn.getpeername(), full_msg))
	# print("the client send :" , full_msg)
	conn.send(full_msg.encode())
	print("[SERVER] ",full_msg)	  # Debug print

def recv_message_and_parse(conn):
	## copy from client
	full_msg = conn.recv(1024).decode()
	print("[CLIENT] ", full_msg)  # Debug print
	cmd, data = chatlib_skeleton.parse_message(full_msg)
	return cmd, data

def print_client_sockets(list_sockets):
	clients = "\n".join([socket.getpeernume()for socket in list_sockets])
	print(clients)


# SOCKET CREATOR

def setup_socket():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	address = (SERVER_IP, SERVER_PORT)
	server_socket.bind(address)
	server_socket.listen()
	
	return server_socket
	

		
def send_error(conn, error_msg):

	build_and_send_message(conn,chatlib_skeleton.PROTOCOL_SERVER["login_failed_msg"],error_msg)

	
##### MESSAGE HANDLING


def handle_logout_message(conn):
	global logged_users
	global client_sockets
	logged_users.pop(conn.getpeername())
	client_sockets.remove(conn)
	conn.close()



def handle_login_message(conn, data):
	"""
	Gets socket and message data of login message. Checks  user and pass exists and match.
	If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
	Recieves: socket, message code and data
	Returns: None (sends answer to client)
	"""
	global users
	global logged_users
	# If a new user is registered and logged in at the same time
	users = load_user_database()

	user_name_and_pass = chatlib_skeleton.split_data(data,1)
	if len(user_name_and_pass ) == 2 :
		if user_name_and_pass[0] in users :
			if user_name_and_pass[1] == users[user_name_and_pass[0]]["password"]:
				build_and_send_message(conn,chatlib_skeleton.PROTOCOL_SERVER["login_ok_msg"],"")
				logged_users[conn.getpeername()]= user_name_and_pass[0]


			else:
				build_and_send_message(conn, chatlib_skeleton.PROTOCOL_SERVER["login_failed_msg"], "The password is incorrect")
		else:
			build_and_send_message(conn, chatlib_skeleton.PROTOCOL_SERVER["login_failed_msg"], "User does not exist")
	else:
		build_and_send_message(conn, chatlib_skeleton.PROTOCOL_SERVER["login_failed_msg"], "please try again .....")




def handle_client_message(conn, cmd, data):
	"""
	Gets message code and data and calls the right function to handle command
	Recieves: socket, message code and data
	Returns: None
	"""
	global logged_users

	if conn.getpeername() in logged_users:
		if cmd == chatlib_skeleton.PROTOCOL_CLIENT["logout_msg"] or cmd == None:
			handle_logout_message(conn)
		elif cmd == chatlib_skeleton.PROTOCOL_CLIENT["high_score"]:
			handle_highscore_message(conn)
		elif cmd == chatlib_skeleton.PROTOCOL_CLIENT["my_score"]:
			handle_getscore_message(conn,logged_users[conn.getpeername()])
		elif cmd == chatlib_skeleton.PROTOCOL_CLIENT["players"]:
			handle_logged_message(conn)
		elif cmd == chatlib_skeleton.PROTOCOL_CLIENT["get_question"]:
			handle_question_message(conn,logged_users[conn.getpeername()])
		elif cmd ==chatlib_skeleton.PROTOCOL_CLIENT["answer"]:
			handle_answer_message(conn,logged_users[conn.getpeername()],data)
		else:
			send_error(conn,"The command is not recognized")

	else:
		if cmd == chatlib_skeleton.PROTOCOL_CLIENT["login_msg"]:
			handle_login_message(conn, data)
		else:
			send_error(conn,"The command is not recognized")
	




def handle_getscore_message(conn,user_name):
	if user_name in users:
		build_and_send_message(conn,chatlib_skeleton.PROTOCOL_SERVER["get_score"],str(users[user_name]["score"]))
	else:
		send_error(conn,"user isn't exist")

def handle_highscore_message(conn):
	temp_dict = dict()
	table_score = ""
	for user in users:
		temp_dict[user] = users[user]['score']

	temp_dict = {k: v for k, v in sorted(temp_dict.items(), key=lambda item: item[1], reverse=True)}

	for user in temp_dict:
		table_score += user +": " + str(temp_dict[user])+"\n"
	build_and_send_message(conn,chatlib_skeleton.PROTOCOL_SERVER["high_score"] , table_score)

def handle_logged_message(conn):
	answer = ""
	for index,user in enumerate(logged_users):
		if index == len(logged_users)-1:
			answer += logged_users[user]
		else:
			answer += logged_users[user] + ", "
	build_and_send_message(conn, chatlib_skeleton.PROTOCOL_SERVER["players_logged"], answer)




def create_random_question (user_name):
	result = ""
	global questions
	global users
	t = [i for i in list(questions.items()) if not i[0] in users[user_name]["questions_asked"]]
	if len(t) == 0:
		return None
	else:
		key, value = random.choice(t)
		users[user_name]["questions_asked"].append(key)
		result += str(key) + "#" + value["question"] + "#"
		for i in value["answers"]:
			result += str(i) + "#"
		result += str(value["correct"])
		return result

	# answers = "#".join(value['answers'])
	# return f"{key}#{value['question']}#{answers}"


def handle_question_message (conn,user_name):
	global logged_users
	question = create_random_question(user_name)
	if question == None:
		build_and_send_message(conn,chatlib_skeleton.PROTOCOL_SERVER["no_question"],"")
	else:
		build_and_send_message(conn,chatlib_skeleton.PROTOCOL_SERVER["your_question"],question)



def update_in_file(user_name):
	global users
	# if A user who has answered all the questions will have the opportunity to receive new questions again
	if len (users[user_name]["questions_asked"]) > 50:
		users[user_name]["questions_asked"] = list()

	with open("C:\\Users\menyb\PycharmProjects\\NetWork.py\Trivia\\u1\\users.txt", 'w') as users_file:
		users_file.write(json.dumps(users))


def handle_answer_message (conn,user_name,data):
	answer = data.split("#")
	if int(answer[0]) in questions:
		if questions[int(answer[0])]["correct"] == answer[1]:
			if user_name in users:
				users[user_name]["score"]+=5
				update_in_file(user_name)
				build_and_send_message(conn,chatlib_skeleton.PROTOCOL_SERVER["correct_answer"],"")
		else:
			build_and_send_message(conn,chatlib_skeleton.PROTOCOL_SERVER["wrong_answer"],str(questions[int(answer[0])]["correct"]))
	else:
		send_error(conn,"question isn't exist..")






def main():
	# Initializes global users and questions dicionaries using load functions, will be used later
	global users
	global questions
	global messages_to_send

	
	print("Welcome to Trivia game!")
	server_socket = setup_socket()
	print("Waiting for a new connection...")
	while True:


		ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, client_sockets,[])
		for current_socket in ready_to_read:
			if current_socket is server_socket:
				(client_socket, client_address) = current_socket.accept()
				print("New client joined!", client_address, "\n")
				client_sockets.append(client_socket)
				# print_client_sockets(client_sockets)
			else:
				cmd, data = recv_message_and_parse(current_socket)

				if  cmd == "" or cmd == None:
					print("Client logged off!", current_socket.getpeername())
					handle_logout_message(current_socket)
					break
				else:
					handle_client_message(current_socket, cmd, data)
		for message in messages_to_send:
			current_socket, data = message
			if current_socket in ready_to_write:
				current_socket.send(data.enconde())
				messages_to_send.remove(message)

	#
		# (client_socket, client_address) = server_socket.accept()
		# print("New client joined!", client_address)
		#
		#
		# while True:
		# 	cmd, data = recv_message_and_parse(client_socket)
		# 	if cmd == chatlib_skeleton.PROTOCOL_CLIENT["logout_msg"] or cmd == None:
		# 		print("Connection closed..")
		# 		break
		# 	handle_client_message(client_socket, cmd, data)



if __name__ == '__main__':
	main()


	