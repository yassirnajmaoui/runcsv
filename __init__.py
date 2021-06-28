import numpy as np
import re
import csv
from matplotlib import pyplot as plt
import random

parse_refs_regex = re.compile("(\*)?{(.*?),(.*?)}")
# Initial size 10x10
s = np.ndarray([10,10], dtype=object)
s.fill("")
p = np.ndarray(s.shape, dtype=object)
o = np.ndarray(s.shape, dtype=object)
f = np.ndarray(s.shape, dtype=object)

def check_pos(i,j):
	if(i<0 or j<0 or i>s.shape[0] or j>s.shape[1]):
		return False
	return True

def parse_cell(i, j):
	if(not check_pos(i,j)):
		return
	current_s = s[i][j][1:] # remove the "=" in the string
	while True:
		delta = 0
		matches = list() # List of matches
		for match in re.finditer(parse_refs_regex, current_s):
			matches.append(match)
		if len(matches) == 0:
			break
		for match in matches:
			ref_groups = match.groups()
			referenced_i_str = ref_groups[-2]
			referenced_j_str = ref_groups[-1]
			resulting_val = ""
			resulting_i = 0
			resulting_j = 0
			# This part could be made to be parsed by another engine instead of using "exec"
			resulting_i = eval(referenced_i_str)
			resulting_j = eval(referenced_j_str)
			if(ref_groups[0] == '*'):
				resulting_val = p[resulting_i][resulting_j]
			else:
				resulting_val = str(f[resulting_i][resulting_j])
			matched_span = match.span()
			current_s = current_s[:matched_span[0]+delta] + resulting_val + current_s[matched_span[1]+delta:]
			# Correct position for next replacement (Because you cannot reverse a callable_terator)
			delta = len(resulting_val) - (matched_span[1]-matched_span[0])
	return current_s


def process_cell(i,j):
	item = s[i][j]
	if item != "" and item[0] == '=':
		p[i][j] = parse_cell(i,j)
		o[i][j] = eval(p[i][j]) # Execution of the generated command
		f[i][j] = str(o[i][j])
	else:
		p[i][j] = s[i][j]
		o[i][j] = p[i][j]
		f[i][j] = str(o[i][j])


