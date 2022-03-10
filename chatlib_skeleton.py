# Protocol Constants

CMD_FIELD_LENGTH = 16	# Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4   # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10**LENGTH_FIELD_LENGTH-1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message

# Protocol Messages 
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
"login_msg" : "LOGIN" ,
"logout_msg" : "LOGOUT" ,
"high_score" : "HIGHSCORE",
"my_score" : "MY_SCORE",
"get_question":"GET_QUESTION",
"answer" : "SEND_ANSWER",
"players" : "LOGGED"
} # .. Add more commands if needed


PROTOCOL_SERVER = {
"login_ok_msg" : "LOGIN_OK",
"login_failed_msg" : "ERROR",
"get_score" : "YOUR_SCORE",
"high_score" : "ALL_SCORE",
"players_logged" : "LOGGED_ANSWER",
"your_question" : "YOUR_QUESTION",
"correct_answer" : "CORRECT_ANSWER",
"wrong_answer" : "WRONG_ANSWER",
"no_question": "NO_QUESTIONS"
} # ..  Add more commands if needed


# Other constants

ERROR_RETURN = None  # What is returned in case of an error


def build_message(cmd, data):
	# """
	# Gets command name (str) and data field (str) and creates a valid protocol message
	# Returns: str, or None if error occured
	# """
	full_msg = ""
	if len(cmd) > CMD_FIELD_LENGTH:
		return None
	if len(data) > MAX_DATA_LENGTH :
		return None
	full_msg += cmd.replace(" ", "")
	full_msg += " "*(16-len(full_msg))+DELIMITER
	full_msg += "0"*(4-len(str(len(data))))+ str(len(data)) + DELIMITER + data
	return full_msg




def parse_message(data):
	"""
	Parses protocol message and returns command name and data field
	Returns: cmd (str), data (str). If some error occured, returns None, None
	"""
	if data.count(DELIMITER) != 2:
		return None,None
	lst = data.split(DELIMITER)
	if (lst[1].replace(" ", "")).isdigit():
		size = int(lst[1])
	else:
		return None,None
	if size != len(lst[2]):
		return None,None
	else:
		return lst[0].replace(" ", ""),lst[2]


	
def split_data(msg, expected_fields):
	"""
	Helper method. gets a string and number of expected fields in it. Splits the string 
	using protocol's data field delimiter (|#) and validates that there are correct number of fields.
	Returns: list of fields if all ok. If some error occured, returns None
	"""
	if msg.count(DATA_DELIMITER) == expected_fields:
		return msg.split(DATA_DELIMITER)
	else:
		return [ERROR_RETURN]


def join_data(msg_fields):

	"""
	Helper method. Gets a list, joins all of it's fields to one string divided by the data delimiter. 
	Returns: string that looks like cell1#cell2#cell3
	"""
	result = ''
	for item in msg_fields:
		result += str(item) + DATA_DELIMITER
	return result[:-1]
