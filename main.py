import numpy as np
import argparse
import csv
import re

# This is only a beginning, this system would be much better
# when implemented using C++ and Pybind11

parser = argparse.ArgumentParser(description='Process a CSV file')
parser.add_argument('-i', help='Input csv file')
parser.add_argument('-o', help='Output csv file')
args = parser.parse_args()

input_file = args.i
output_file = args.o

s_l = []

# TODO: Check if amount of rows is always constant
with open(input_file, newline='') as f:
    reader = csv.reader(f)
    s_l = list(reader)


i=0
j=0
s = np.array(s_l, dtype=object)
print("Input:")
print(s)
p = np.ndarray(s.shape, dtype=object)
o = np.ndarray(s.shape, dtype=object)
f = np.ndarray(s.shape, dtype=object)

# TODO: When referencing with *{...} in a "future",
# the value referenced doesn't have the "=" stripped
# Possibly dirty fix: strip them all beforehand?

# TODO: Detect recursive loops

# TODO: Make the software work with numpy arrays instead of
# lists so that the user can do fancy selections

parse_refs_regex = re.compile("(\*)?{(.*?),(.*?)}")

for row in s:
    j=0
    for item in row:
        if item is not "" and item[0] == '=':
            s[i][j] = item[1:] # remove the "=" in the string
            current_s = s[i][j]
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
                    exec("resulting_i = " + referenced_i_str)
                    exec("resulting_j = " + referenced_j_str)
                    if(ref_groups[0] == '*'):
                        resulting_val = s[resulting_i][resulting_j]
                    else:
                        resulting_val = f[resulting_i][resulting_j]
                    matched_span = match.span()
                    current_s = current_s[:matched_span[0]+delta] + resulting_val + current_s[matched_span[1]+delta:]
                    # Correct position for next replacement (Because you cannot reverse a callable_terator)
                    delta = len(resulting_val) - (matched_span[1]-matched_span[0])
            p[i][j] = current_s
            o[i][j] = eval(p[i][j]) # Execution of the generated command
            f[i][j] = str(o[i][j])
        else:
            p[i][j] = s[i][j]
            o[i][j] = p[i][j]
            f[i][j] = str(o[i][j])
        j+=1
    i+=1

with open(output_file, 'w') as file:
    # using csv.writer method from CSV package
    writer = csv.writer(file)
    writer.writerows(f)

print(f)
