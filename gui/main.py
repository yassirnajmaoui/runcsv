from os import set_blocking
import sys
from PyQt5.QtCore import(
	QModelIndex,
	QRect,
	QItemSelectionModel
)
import numpy as np
import re
import csv
from PyQt5.QtGui import (
	QStandardItemModel
)
from PyQt5.QtWidgets import (
	QApplication,
	QDesktopWidget,
	QVBoxLayout,
	QPushButton,
	QWidget,
	QTableView,
	QTableWidget,
	QLineEdit,
	QTableWidgetItem,
)

# Priorities:
# TODO ASAP: Save file and Open file
# TODO: Fancy selection
# TODO: Quality of life like:
#	- Return should go down one cell
#	- Delete button for cells (s[...:...,...:...])
#	- Other useful usages

####################################################################
# THIS SECTION CANNOT BE ELSEWHERE FROM HERE
# THIS IS THE SPREADSHEET ENGINE

# Initial size
nbRows = 10
nbCols = 10

parse_refs_regex = re.compile("(\*)?{(.*?),(.*?)}")
s = np.ndarray([nbCols,nbRows], dtype=object)
s.fill("")
print("Input:\n"+str(s))
p = np.ndarray(s.shape, dtype=object)
o = np.ndarray(s.shape, dtype=object)
f = np.ndarray(s.shape, dtype=object)

def check_pos(i,j):
	if(i<0 or j<0 or i>nbRows or j>nbCols):
		return False
	return True

def parse_cell(source_str, i, j):
	if(not check_pos(i,j)):
		return
	current_s = source_str
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
				resulting_val = s[resulting_i][resulting_j]
				if resulting_val[0] == "=":
					resulting_val = resulting_val[1:]
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
		curr_s = item[1:] # remove the "=" in the string
		p[i][j] = parse_cell(curr_s,i,j)
		o[i][j] = eval(p[i][j]) # Execution of the generated command
		f[i][j] = str(o[i][j])
	else:
		p[i][j] = s[i][j]
		o[i][j] = p[i][j]
		f[i][j] = str(o[i][j])





# END 0F SPREADSHEET ENGINE
####################################################################


class MainWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("A spreadsheet better than Microsoft Incel")
		self.ci=0
		self.cj=0

		# Window geometry
		self.setGeometry(100, 100, 1024, 640)
		qtRectangle = self.frameGeometry()
		avGeo = QDesktopWidget().availableGeometry()
		centerPoint = avGeo.center()
		qtRectangle.moveCenter(centerPoint)
		self.move(qtRectangle.topLeft())
		#self.setGeometry(avGeo)

		# Formula editor
		self.formulaEdit = QLineEdit()
		self.formulaEdit.textChanged.connect(self.onFormulaChange)
		self.formulaEdit.returnPressed.connect(self.formulaReturnPress)

		# Table
		self.tableView = QTableWidget(self)
		self.tableView.setRowCount(nbRows)
		self.tableView.setColumnCount(nbCols)
		self.tableView.setHorizontalHeaderLabels([str(i) for i in range(nbRows)])
		self.tableView.setVerticalHeaderLabels([str(i) for i in range(nbCols)])
		self.tableView.clicked.connect(self.onCellClicked)

		# Run button
		self.runBtn = QPushButton("Run")
		self.runBtn.clicked.connect(self.runSheet)

		# Create a QHBoxLayout instance
		layout = QVBoxLayout()
		# Add widgets to the layout
		layout.addWidget(self.formulaEdit)
		layout.addWidget(self.tableView)
		layout.addWidget(self.runBtn, 2)
		# Set the layout on the application's window
		self.setLayout(layout)
		print(self.children())
	
	def onCellClicked(self, index=None):
		self.ci = index.row()
		self.cj = index.column()
		self.formulaEdit.setFocus()
		self.formulaEdit.setText(s[self.ci][self.cj])
		print(self.ci,self.cj)
	
	def onFormulaChange(self):
		s[self.ci][self.cj] = self.formulaEdit.text()
	
	def formulaReturnPress(self, key=None):
		self.affectCell(self.ci,self.cj)
		#self.ci+=1
		#self.tableView.setSelection(QRect(self.ci,self.cj,self.ci+1,self.cj+1), QItemSelectionModel.SelectionFlag.SelectCurrent)
	
	def runSheet(self):
		for i in np.arange(s.shape[0]):
			for j in np.arange(s.shape[1]):
				self.affectCell(i,j)
	
	def affectCell(self,i,j):
		try:
			process_cell(i,j)
			newitem = QTableWidgetItem(f[i][j])
			self.tableView.setItem(i,j, newitem)
		except:
			print("There was an error in cell {"+str(i)+","+str(j)+"}")



if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())

