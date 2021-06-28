#!/usr/bin/python3
import numpy as np
import re
import csv
from matplotlib import pyplot as plt

# Initial size
nbRows = 10
nbCols = 10

global s,p,o,f
parse_refs_regex = re.compile("(\*)?{(.*?),(.*?)}")
s = np.ndarray([nbCols,nbRows], dtype=object)
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


# END OF ENGINE HERE (Had to be pasted instead of imported due to global variable issues in Python)

import argparse

parser = argparse.ArgumentParser(description='Process a CSV file')
parser.add_argument('-i', help='Input csv file')
parser.add_argument('-o', help='Output csv file')
args = parser.parse_args()

input_file = args.i
output_file = args.o

#s_l = []
with open(input_file, 'r', newline='') as file:
	reader = csv.reader(file)
	s_l = list(reader)

s_l_arr = np.array(s_l, dtype=object)
print(s_l_arr.shape)
s.resize(s_l_arr.shape,refcheck=False)
s[:,:] = np.copy(s_l_arr)
p.resize(s.shape,refcheck=False)
o.resize(s.shape,refcheck=False)
f.resize(s.shape,refcheck=False)

for i in np.arange(s.shape[0]):
	for j in np.arange(s.shape[1]):
		process_cell(i,j)

with open(output_file, 'w+') as file:
	writer = csv.writer(file)
	writer.writerows(f)

print(f)



