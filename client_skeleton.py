import ast
import chatlib_skeleton
import socket
import json

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678

# HELPER SOCKET METHODS
#
def build_and_send_message(client_socket, code, data):


	# Builds a new message using chatlib, wanted code and message.
	# Prints debug info, then sends it to the given socket.
	# Paramaters: conn (socket object), code (str), data (str)
	# Returns: Nothing


    full_msg = chatlib_skeleton.build_message(code,data)
    # print("the client send :" , full_msg)
    client_socket.send(full_msg.encode())


def recv_message_and_parse(client_socket):

    # """
	# Recieves a new message from given socket,
	# then parses the message using chatlib.
	# Paramaters: conn (socket object)
	# Returns: cmd (str) and data (str) of the received message.
	# If error occured, will return None, None
	# """

    full_msg = client_socket.recv(1024).decode()
    cmd, data = chatlib_skeleton.parse_message(full_msg)
    return cmd,data



def connect():
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    address = (SERVER_IP,SERVER_PORT)
    client_socket.connect(address)
    return client_socket


def error_and_exit(error_msg):
    # Implement code
    print(error_msg)
    exit()


def login(conn):


    while True:
        username = input("Please enter User Name: \n")
        password = input("Please enter Password: \n")
        full_msg = username+'#'+password
        build_and_send_message(conn, chatlib_skeleton.PROTOCOL_CLIENT["login_msg"],full_msg)
        cmd ,data = recv_message_and_parse(conn)
        print(f"server send :{cmd}!\n")
        if data != "" :
            print(f"{data}")
        if  cmd == "LOGIN_OK" :
            break
        print("Please try again ...")

def logout(conn):
    build_and_send_message(conn,chatlib_skeleton.PROTOCOL_CLIENT["logout_msg"],"")
    conn.close()
    print("LOG-OUT...")


def build_send_recv_parse (client_socket, code, data):
    build_and_send_message(client_socket,code,data)
    msg_code ,msg = recv_message_and_parse(client_socket)
    return msg_code,msg

def get_score (client_socket):
    cmd, data = build_send_recv_parse(client_socket, chatlib_skeleton.PROTOCOL_CLIENT["my_score"], "")
    print(f"server send->\n{cmd}:\n{data}\n")


def get_highscore(client_socket):
    cmd, data =  build_send_recv_parse(client_socket,chatlib_skeleton.PROTOCOL_CLIENT["high_score"],"")
    print(f"server send->\n{cmd}:\n{data}\n")

def play_question (client_socket):
    cmd, data = build_send_recv_parse(client_socket, chatlib_skeleton.PROTOCOL_CLIENT["get_question"], "")
    if cmd == "NO_QUESTIONS":
        print("GAME OVER!")
        return
    else:
        q_lst = data.split("#")
        print(f"Question number {q_lst[0]}:")
        print(f"Q:{q_lst[1]} :")
        if len(q_lst) >= 5:
            print(f"\t 1. {q_lst[2]}")
            print(f"\t 2. {q_lst[3]}")
            i=2
        if len(q_lst) > 5:
            print(f"\t 3. {q_lst[4]}")
            print(f"\t 4. {q_lst[5]}")
            i=4
        while True:
            answer = input(f"Please choose an answer [1-{i}]:\n")
            if answer.isdigit() and int(answer) >=1 and int(answer) <= i:
                cmd, data = build_send_recv_parse(client_socket, chatlib_skeleton.PROTOCOL_CLIENT["answer"], q_lst[0] + "#" + q_lst[int(answer)+1])
                if cmd == "CORRECT_ANSWER" :
                    print("YES!!!")
                else :
                    print(f"Nope, correct answer is {data}..")
                break




def get_logged_users (client_socket):
    cmd, data = build_send_recv_parse(client_socket, chatlib_skeleton.PROTOCOL_CLIENT["players"], "")
    print(f"logged users:\n{data}")

def create_account(client_socket):
    users_dict = {}
    f = open("C:\\Users\menyb\PycharmProjects\\NetWork.py\Trivia\\u1\\users.txt", "r")
    users = f.read()
    users_dict = ast.literal_eval(users)
    f.close()
    while True:
        username = input("Please enter username: \n")
        if not username in users_dict:
            break
        print("Busy user name Choose another one... ")
    password = input("Please enter password: \n")
    users_dict[username] = {"password":password , "score" : 0, "questions_asked" : []}

    print(users_dict)

    with open("C:\\Users\menyb\PycharmProjects\\NetWork.py\Trivia\\u1\\users.txt", 'w') as users_file:
        users_file.write(json.dumps(users_dict))
    login(client_socket)


def main():
    client_socket = connect()
    answer = ""
    while True:
        answer = input("Create Account/Login : [c/l]\n")
        if answer == 'l':
            login(client_socket)
            break
        if answer == 'c':
            create_account(client_socket)
            break



    req = ""
    while True:
        print("p          Play a trivia question")
        print("s          Get my score")
        print("h          Get high score")
        print("l          Get logged users")
        print("q          Quit\n")
        req = input("Please enter your choice:\n")
        if req == 's':
            get_score(client_socket)
        elif req == 'p' :
            play_question(client_socket)
        elif req == "h":
            get_highscore(client_socket)
        elif req == "l":
            get_logged_users(client_socket)
        elif req == "q" or req == "":
            logout(client_socket)
            break
        else:
            print("\tPlease try again ...\n\n")




if __name__ == '__main__':
    main()

