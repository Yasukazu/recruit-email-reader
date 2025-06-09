# divide recruits
from typing import TextIO
from dataclasses import dataclass
import sys
from enum import Enum
import re
from collections import deque
from pprint import pp

HEARDER_LINE = '==='
END_LINE = '---'

LINE_FEEDER = sys.stdin

IN_HEADER = False

@dataclass
class Header:
	START = "募集内容"
	num: int
	branch_job: str
@dataclass

class HeaderContent:
	header: Header
	content: list[str]

HEADER_CONTENT_LIST: list[HeaderContent] = []

class TextEndException(Exception):
	pass
class HeaderEnd(TextEndException):
	pass
class ContentEnd(TextEndException):
	pass

class LineSeparator(Enum):
	HEARDER_LINE_SEP = '='
	END_LINE_SEP = '-'

def is_separator(line: str):
	for sep in list(LineSeparator):
		cc = {c == sep.value for c in line}
		if len(cc) == 1:
			tf = cc.pop()
			if tf:
				return sep

LINES: deque[str] = deque()
def load():
	while (line:=LINE_FEEDER.readline()):
		LINES.append(line.strip())
	LINES.reverse()

def divide():
	leading = divide_start()
	while (header_line := get_header()):
		header = load_header([header_line])
		content = get_content()
		header_content = HeaderContent(header=header, content=content)
		pp(header_content.header)
		print()
	print()
	print()
	print(leading)

def divide_start():
	leading = []
	while (len(LINES) > 1):
		line = LINES.pop()
		leading.append(line)
		if not line:
			continue
		sep = is_separator(line)
		if sep:
			match sep:
				case LineSeparator.END_LINE_SEP:
					raise EOFError("End of contents.")
				case LineSeparator.HEARDER_LINE_SEP:
					# LINES.append(line)
					return leading
	raise ValueError("No Header line!")

def get_header():
	header = None
	while len(LINES) > 0:
		line = LINES.pop()
		if not line:
			continue
		sep = is_separator(line)
		if sep:
			match sep:
				case LineSeparator.END_LINE_SEP:
					raise EOFError("End of contents.")
				case LineSeparator.HEARDER_LINE_SEP:
					raise ValueError("No Header line!")	
		else:
			header = line
			break
	if not header:
		raise ValueError("No Header line!")	
	while len(LINES) > 0:
		line = LINES.pop()
		if not line:
			continue
		sep = is_separator(line)
		if sep:
			match sep:
				case LineSeparator.END_LINE_SEP:
					raise EOFError("End of contents.")
				case LineSeparator.HEARDER_LINE_SEP:
					return header
	raise ValueError("No closing Header line!")	

def get_content():
	content = []
	while len(LINES) > 0:
		line = LINES.pop()
		sep = is_separator(line)
		if sep:
			match sep:
				case LineSeparator.END_LINE_SEP:
					raise EOFError("End of contents.")
				case LineSeparator.HEARDER_LINE_SEP:
					break
		else:
			content.append(line)
	if not content:
		raise ValueError("No content!")	
	return content

def load_header(lines):
	line = None
	for n, line in enumerate(lines):
		if line:
			break

	if not line:
		raise ValueError('No header content found!')
	line = line.replace('　', ' ')
	tokens = line.split(maxsplit=1)

	i = -1
	for i, c in enumerate(tokens[0]):
		if c.isdigit():
			break
	if i < 0:
		raise ValueError("No Bosyu number!")
	return Header(int(tokens[0][i:]), tokens[1])


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Needs filespec")
		sys.exit(1)
	with open(sys.argv[1]) as fi:
		LINE_FEEDER = fi
		load()
		divide()