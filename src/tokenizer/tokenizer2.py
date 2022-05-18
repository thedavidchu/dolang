from enum import Enum
from typing import Tuple


EOF: str = None


class TokenType(str, Enum):
	WHITESPACE = "WHITESPACE"	# Indent vs non-indent
	COMMENT = "COMMENT"	# Multi-line vs non-multiline, nesting
	STRING = "STRING"	# Multi-quotes, single-vs-double quote
	LITERAL = "LITERAL"	# Keyword, non-keyword
	NUMBER = "NUMBER"	# Float, int, complex
	PUNCTUATION = "PUNCTUATION"	# Stand-alone, non-standalone


class Text:
	def __init__(self, text: str):
		self.text = text
		self.current_idx = 0
		self.current_lineno = 1
		self.current_colno = 0

	def __next__(self):
		c = self.text[self.current_idx]
		if c == "\n":
			self.current_lineno += 1
			self.current_colno = 0
		else:
			self.current_colno += 1
		self.current_idx += 1
		return self.text[self.current_idx]

	def getoffset(self, idx):
		if len(self.text) > self.current_idx + idx:
			return self.text[self.current_idx:self.current_idx + idx]
		else:
			return EOF

	def getpos(self):
		return self.current_idx, self.current_lineno, self.current_colno


class Token:
	def __init__(self, strtoken: str, ttype: TokenType, startpos: Tuple[int, int, int], endpos: Tuple[int, int, int]):
		self.strtoken: str = strtoken
		self.ttype: TokenType = ttype
		self.startpos: Tuple[int, int, int] = startpos
		self.endpos: Tuple[int, int, int] = endpos

	def __repr__(self) -> str:
		return f"{self.startpos[1]}:{self.startpos[2]}-{self.endpos[1]}:{self.endpos[2]}:\t{self.ttype}\t{self.strtoken}"


"""
Steps
-----

1. Identify if it _could_ be a certain class.
2. Try to capture the token. If it is the correct class, we return a Token
object. Otherwise, we will return None.
"""


################################################################################
########## START IDENTIFICATION FUNCTIONS ######################################
################################################################################
def is_whitespace_start(text: Text) -> bool:	# [ \n\t\v\r]+
	"""Note: the word "_start" in the function name is unnecessary. It is the
	start, the middle, and the end, because all characters fall into the same
	group."""
	c = text.getoffset(0)
	assert c != EOF
	return c.whitespace()


def is_comment_start(text: Text) -> bool:
	c = text.getoffset(0)
	next_c = text.getoffset(1)
	assert c != EOF
	elif c == "#":
		return True
	# Assuming next_c is not EOF... not that it would matter.
	elif c == "/" and (next_c == "*" or next_c == "/"):
		return True
	return False


def is_string_start(text: Text):
	"""We will only support strings surrounded by single double quotes for now."""
	c = text.getoffset(0):
	assert c != EOF
	return c == "\""


def is_number_start(text: Text):
	"""We will not support 0. or .0 numbers for now. + 10 is also not a single number."""
	c = text.getoffset(0)
	next_c = text.getoffset(1)
	assert c != EOF
	if c.isdecimal():
		return True
	elif c == "+" or c == "-":
		# Assuming next_c is not EOF... not that it would matter.
		return next_c.isdecimal()	# [0-9]
	return False


def is_literal_start(text: Text):
	c = text.getoffset(0)
	assert c != EOF
	return c.isalpha() or c == "_"


def is_standalone_punctuation_start(text: Text):	# [()[]{},;]
	"""Note: the word "_start" in the function name is unnecessary. It is the
	start, the middle, and the end, because this is only one character."""
	c = text.getoffset(0)
	assert c != EOF
	return c in {"(", ")", "[", "]", "{", "}", ";", ","}


def is_groupable_punctuation_start(text: Text):
	"""The punctuation characters _can_ be grouped, e.g. +=, **=, etc."""
	c = text.getoffset(0)
	assert c != EOF
	if c in "~!@$%^&*-+=|:<>./?":
		return True
	return False


################################################################################
########## EXTRACTION FUNCTIONS ################################################
################################################################################
def capture_whitespace(text: Text) -> "Token | None":
	c = text.getoffset(0)
	assert c != EOF

	startpos = text.getpos()
	i = 0
	while c.whitespace():
		i += 1
		c = text.getoffset(i)

	strtoken = text.text[text.current_idx:text.current_idx + i]
	for _ in range(i):
		next(text)
	endpos = text.getpos()

	token = Token(strtoken=strtoken, ttype=TokenType.WHITESPACE, startpos=startpos, endpos=endpos)
	return token


def capture_comment(text: Text) -> "Token | None":
	"""Types of comments:
	# This ends in \n or EOF.
	// This ends in \n or EOF.
	/* This can next but cannot end without its ending, which is */.
	"""
	c = text.getoffset(0)
	next_c = text.getoffset(1)
	assert c != EOF

	startpos = text.getpos()
	if c == "#":
		start_comment = "#"
	elif c == "/" and next_c == "/":
		start_comment = "//"
	elif c == "/" and next_c == "*":
		start_comment = "/*"
	else:
		raise ValueError("unexpected comment starter")

	raise NotImplemented()
	

################################################################################
########## MAIN FUNCTIONS ######################################################
################################################################################
def main():
	with open("parser.py") as f:
		text = Text(f.read())

	tokens = []
	c = text.getoffset(0)
	while c != EOF:
		if is_whitespace_start(c):
			t = capture_whitespace(text)
			if t is not None:
				tokens.append(t)
				# Run this after every iteration
				c = next(text)
				continue
			# Otherwise, failure to capture whitespace
		if is_comment_start(c):
			t = capture_comment(text)
			if t is not None:
				tokens.append(t)
				# Run this after every iteration
				c = next(text)
				continue
			# Otherwise, failure to capture comment
		# Run this after every iteration
		c = next(text)
		continue

if __name__ == "__main__":
	main()
