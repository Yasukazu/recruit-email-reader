# divide recruits
from typing import TextIO
from dataclasses import dataclass
import sys
from enum import Enum
import re
from collections import deque
from pprint import pp
from pathlib import Path
from unicodedata import normalize

HEARDER_LINE = '==='
END_LINE = '---'

LINE_FEEDER = sys.stdin

IN_HEADER = False



DATE_TIME_BRACKET_PAIR = '【】'
WEEKDAYS_KANJI = '日月火水木金土'

class JobDateTime(Enum):
	KIKAN = ('募集期間', re.compile(rf"(\d+)/(\d+)\(([{WEEKDAYS_KANJI}])\)"), '')
	JIKAN = ('時間', re.compile(r"(\d+):(\d+)-(\d+):(\d+)"), "勤務可能な方")

	def bracket(self):
		return f"【{self.value[0]}】"
	def pattern(self):
		return self.value[1]
	def find_all(self, s: str):
		sub_s = re.sub(r'[~〜～]', '-', s)
		norm_arg = normalize('NFKC', sub_s)
		return self.value[1].findall(norm_arg)
@dataclass
class Header:
	START = "募集内容"
	num: int
	branch_job: str

@dataclass
class FromToDate:
	frm: tuple[str, str, str]
	to: tuple[str, str, str]

@dataclass
class Jikan:
	frm_to: tuple[str, str, str, str]
@dataclass
class HeaderContent:
	header: Header
	content: list[str]
	def kikan_list(self):
		found = False
		kikan_bracket = JobDateTime.KIKAN.bracket() 
		for m, line in enumerate(self.content):
			if kikan_bracket == line.strip():
				found = True
				break
		if not found:
			raise ValueError("No kikan title found!")
		kikan_list: list[FromToDate] = []
		kikan_match = JobDateTime.KIKAN.find_all
		jikan_bracket = JobDateTime.JIKAN.bracket()
		jikan_found = False
		for n, line in enumerate(self.content[m+1:]):
			if (mch:=kikan_match(line.strip())):
				for mc in mch:
					ftd = FromToDate(*mc) # h.groups()[0:3],mch.groups()[3:6])
					kikan_list.append(ftd)
			elif line.strip() == jikan_bracket:
				jikan_found = True
				break
		if not kikan_list:
			raise ValueError("No kikan(s) found!")
		if not jikan_found:
			raise ValueError("No jikan found!")
		return kikan_list, n + m
		
	def get_jikan(self, m: int):
		assert self.content[m+1] == JobDateTime.JIKAN.bracket() 
		jikan_match = JobDateTime.JIKAN.find_all
		jikan = None
		for n, line in enumerate(self.content[m+1:]):
			if (mch:=jikan_match(line.strip())):
				#groups = mch.groups()
				jikan = Jikan(mch)#groups)
				break
		if not jikan:
			raise ValueError("No jikan found!")
		return jikan


		

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
	count = 0
	while (header_line := get_header()):
		header = load_header([header_line])
		content, end_line = get_content()
		header_content = HeaderContent(header=header, content=content)
		kk_list, kikan_pos = header_content.kikan_list()
		jikan = header_content.get_jikan(kikan_pos)
		print(f"{count+1}: {header_content.header=}, {kk_list=}, {jikan=}")
		print()
		if end_line:
			break
		count += 1
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
	closing_header_line = False
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
					closing_header_line = True
					break
		else:
			header += line
	if not closing_header_line:
		raise ValueError("No closing Header line!")	
	return header

def get_content():
	content = []
	end_line = False
	while len(LINES) > 0:
		line = LINES.pop()
		sep = is_separator(line)
		if sep:
			match sep:
				case LineSeparator.END_LINE_SEP:
					end_line = True
					break
				case LineSeparator.HEARDER_LINE_SEP:
					break
		else:
			content.append(line)
	if not content:
		raise ValueError("No content!")	
	return content, end_line

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
	for f in Path().cwd().parent.iterdir():
		break
	ini_file = f
	with ini_file.open() as fi:
		LINE_FEEDER = fi
		load()
		divide()
