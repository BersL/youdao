#!/usr/bin/env python
#coding=utf-8
import sys, tty, termios

#Key = Enum('Key', ('Up', 'Down', 'Left', 'Right', 'Return', 'Tab', 'Other'))

class Key:
	Up = 0
	Down = 1
	Left = 2
	Right = 3
	Return = 4
	Tab = 5
	Other = 6

def getch():
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)
	ch = ''
	try:
		tty.setcbreak(sys.stdin.fileno())
		ch = sys.stdin.read(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	return ch;
	
def getctrch():
	ch = getch()
	if ch == '[':
		ch2 = getch();
		if(ch2 == 'A'):
			return Key.Up
		elif(ch2 == 'B'):
			return Key.Down
		elif(ch2 == 'C'):
			return Key.Right
		elif(ch2 == 'D'):
			return Key.Left
	elif ch == '\t':
		return Key.Tab
	elif ch == '\n':
		return Key.Return
	else:
		return Key.Other

def hide_cursor():
	sys.stdout.write('\033[?25l')
	sys.stdout.flush()
	
def show_cursor():
	sys.stdout.write('\033[?25h')
	sys.stdout.flush()

def cursor_up(line = 1):
	sys.stdout.write('\033[%dA'%line)
	sys.stdout.flush()
	
def cursor_down(line = 1):
	sys.stdout.write('\033[%dB'%line)
	sys.stdout.flush()
	
def cursor_right(line = 1):
	sys.stdout.write('\033[%dC'%line)
	sys.stdout.flush()
	
def cursor_left(line = 1):
	sys.stdout.write('\033[%dD'%line)
	sys.stdout.flush()
	
class Color:
	Red = 31
	Green = 32
	Cyan = 36
	White = 37
	
_lines = {0 : 0}
_cursor_x = 0
_cursor_y = 0

def str_len(str):  
	try:  
		row_l=len(str)  
		utf8_l=len(str.encode('utf-8'))  
		return (utf8_l-row_l)/2+row_l  
	except:
		utf8_l = len(str.decode('utf-8'))
		return (utf8_l-row_l)/2+row_l
	return None  
	
def output(text, newline = False, color = Color.White, bold = False, highlight = False):
	global _cursor_y, _cursor_x, _lines
	esc = '\033['
	if bold: esc += '1;'
	if highlight:
		if color != Color.White: esc += '47;'
		else: esc += '30;47;'
	if color != Color.White: 
		esc += str(color)
	
	if color == Color.White and not bold and not highlight: sys.stdout.write(text)
	else: sys.stdout.write('%sm%s\033[0m'%(esc, text))
	
	_cursor_x += str_len(text)
	try: cur_line = _lines[_cursor_y]
	except: cur_line = 0
	if _cursor_x > cur_line:
		_lines[_cursor_y] = _cursor_x
	
	if newline: outputnl()
	
def outputrt():
	global _cursor_x
	sys.stdout.write('\r')
	_cursor_x = 0
	
def flush():
	sys.stdout.flush()
	
def outputnl():
	global _cursor_y, _cursor_x
	sys.stdout.write('\n')
	_cursor_y += 1
	_cursor_x = 0
	

def move(x, y):
	global _cursor_y, _cursor_x, _lines
	try: 
		if x > _lines[y]-1: x = _lines[y]-1
	except:
		pass
	
	if(_cursor_x > x):
		cursor_left(_cursor_x - x)
	elif(_cursor_x < x): 
		cursor_right(x - _cursor_x)
	
	if(_cursor_y > y): 
		cursor_up(_cursor_y - y)
	elif(_cursor_y < y): 
		cursor_down(y - _cursor_y)
	
	_cursor_x = x
	_cursor_y = y
	
def get_pos():
	global _cursor_x, _cursor_y
	return _cursor_x, _cursor_y
	
if __name__ == '__main__':
	output('Console Input and Output Module', newline = True)
	output('Color Test', color = Color.Cyan, newline = True)
	output('Highlight Test', highlight = True, newline = True)
		
	