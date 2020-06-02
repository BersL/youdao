#!/usr/bin/env python
#coding:utf-8
import sys, os, signal, atexit
import requests
from optparse import OptionParser
from bs4 import BeautifulSoup
from . import conio

youdao = 'http://dict.youdao.com/w/eng/'
wordcnt = 1

all_words = []

def processword(word):
	newword = []
	for exp in word:
		try: exp = exp.replace(u'；', ';').replace(u'（', '(').replace(u'）',')')
		except: pass
		exps = exp.split(';')
		for exp in exps:
			newword.append(exp)
	return newword
		

def printword(word):
	if(len(word)==0):
		return
	word = processword(word)
	if word[0] != '':
		conio.output(word[0], color = conio.Color.Cyan)
		conio.output(' ')
	if len(word) > 1:
		for exp in word[1:]:
			x, y = conio.get_pos()
			all_words.append((exp, x, y))
			conio.output(exp+'; ')
	conio.outputnl()

querying = False
def lookupwords(words):
	global querying
	querying = True
	soups = []
	for word in words:
		resp = requests.get(youdao + word)
		soups.append(BeautifulSoup(resp.text, "html.parser"))
	querying = False
	return soups
		
def processsoup(keyword, soup, specialty, web):
	global wordcnt
	# 拼音/音标
	try:
		h2 = soup.find('h2', class_='wordbook-js')
		phonetic = h2.find('span', class_='phonetic')
		conio.output('%d. %s ' % (wordcnt, keyword), color = conio.Color.Green, bold = True)
	except:
		conio.output('%d. %s ' % (wordcnt, keyword), color = conio.Color.Green, bold = True)
		
	try:
		conio.output(phonetic.string, newline = True, bold = True)
	except:
		conio.outputnl()
		
	wordcnt += 1
	# 释义
	try:
		phrslist = soup.find('div', id='phrsListTab').find('div', class_='trans-container').find('ul')
		wordGrouplist = phrslist.find_all('p', class_='wordGroup')
		if len(wordGrouplist) > 0:
			for wordGroup in wordGrouplist:
				word = []
				attr = wordGroup.span.string
				if attr is None: attr = '释义.'
				word.append(attr.strip())
				exps = wordGroup.find_all('a', class_='search-js')
				for exp in exps:
					word.append(exp.string.strip())
				printword(word)
		else:
			translist = phrslist.find_all('li')
			if len(translist) > 0:
				for trans in translist:
					word = []
					transtext = trans.string
					attrindex = transtext.find('.')
					if(attrindex>=0):
						word.append(transtext[0:attrindex+1])
						word.append(transtext[attrindex+2:])
					else:
						word.append('释义.')
						word.append(transtext)
					printword(word)
			else:
				raise Exception
	except:
		conio.output('无释义', color = conio.Color.Red, newline = True)
	
	# 网络释义
	if(web):
		try:
			tWebTrans = soup.find('div', id='tWebTrans').find_all('div', class_='wt-container')
			if len(tWebTrans) == 0: raise Exception
			word = ['网络释义.']
			for wt in tWebTrans:
				title = wt.find('div', class_='title')
				word.append(title.span.string.strip())
			printword(word)
		except:
			conio.output('无网络释义', color = conio.Color.Red, newline = True)
	# 专业释义
	if(specialty):
		try:
			tPETrans = soup.find('div', id='tPETrans')
			typelist = soup.find('div', id='tPETrans-type-list').find_all('a', class_='p-type')
			rel = ''
			for ptype in typelist:
				if(ptype.string == u'计算机科学技术'):
					rel = ptype['rel'][0]
			if(rel == ''):
				raise Exception
			else:
				translist = tPETrans.find('ul', id='tPETrans-all-trans').find_all('li')
				for trans in translist:
					if(trans['class'][0] == rel):
						word = ['计算机释义.']
						itemlist = trans.find_all('div', class_='items')
						for item in itemlist:
							word.append(item.span.string.strip())
						printword(word)
		except:
			conio.output('无计算机专业释义', color = conio.Color.Red, newline = True)

selected_exp = ''

def copytoclipboard(text):
	try: os.system('echo "%s" | tr -d "\n" | pbcopy' % text)
	except: os.system('echo "%s" | tr -d "\n" | pbcopy' % text.encode('utf-8'))
	
def restore_cursor():
	conio.show_cursor()
	if(len(all_words) > 0):
		word, x, y = all_words[len(all_words)-1]
		conio.move(0, y+2)
	if(selected_exp != ''):
		try: prompt = '"%s" has been copied to clipboard.' % selected_exp
		except: prompt = '"%s" has been copied to clipboard.' % selected_exp.encode('utf-8')
		conio.output(prompt, newline = True, bold = True)
	
def exp_selection():
	global selected_exp
	if(len(all_words) == 0): return
	word, x, y = all_words[0]
	conio.move(x, y)
	conio.output(word, highlight = True)
	conio.flush()
	
	i = 0
	orig = 0
	key = conio.getctrch()
	while(key != conio.Key.Return):
		orig = i
		if key == conio.Key.Other:
			key = conio.getctrch()
			continue
		elif key in (conio.Key.Tab, conio.Key.Right, conio.Key.Down):
			i += 1
			if(i > len(all_words)-1): i = 0
		elif key in (conio.Key.Left, conio.Key.Up):
			i -= 1
			if(i < 0): i = len(all_words)-1
			
		origword, origx, origy = all_words[orig]
		word, x, y = all_words[i]
		conio.move(origx, origy)
		conio.output(origword, highlight = False)
		conio.move(x, y)
		conio.output(word, highlight = True)
		conio.flush()
		key = conio.getctrch()
	word, x, y = all_words[i]
	conio.move(x, y)
	conio.output(word, highlight = False)
	conio.flush()
	selected_exp = word
	copytoclipboard(word)

def _main(argv):
	# options
	usage =	'Usage: %prog [options] <word>...\n'\
			'Look up given words on youdao dictionary.\n'\
			'Word selection mode will be entered after querying. '\
			'Enter return to exit and copy the selected explanation into clipboard.'
	parser = OptionParser(usage=usage, version="%prog 1.0")

	parser.add_option('-s', '--specialty', action="store_true", dest="specialty", 
					default=False, help="show specialty translation of computer science")
	parser.add_option('-w', '--web', action="store_true", dest="web", 
					default=False, help="show more translation of web")
	parser.add_option('-n', '--no_selection', action="store_true", dest="selection", 
					default=False, help="do not enter word selection mode after querying")
	(options, args) = parser.parse_args()
	if len(args) == 0:
		conio.output('No input words. Type -h for help.', newline = True)
		sys.exit(0)
	
	conio.hide_cursor()
	atexit.register(restore_cursor)
	
	conio.output('Querying...', color = conio.Color.Green, bold = True)
	conio.flush()
	soups = lookupwords(args)
	conio.output('\r            ')
	conio.outputrt()
	# 处理单词
	for i in range(0, len(soups)):
		processsoup(args[i], soups[i], options.specialty, options.web)
	
	if not options.selection:
		exp_selection()
	
	return
	
def interrupthandler(signal, frame):
	if querying:
		conio.outputnl()
		conio.output('Keyboard interrupt querying.', newline = True, bold = True)
	sys.exit(0)

def main():
	signal.signal(signal.SIGINT, interrupthandler)
	_main(sys.argv)

if __name__ == '__main__':
	main()
