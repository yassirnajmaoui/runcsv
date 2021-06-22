from os import set_blocking
import sys

from PyQt5.QtCore import(
	Qt,
	QModelIndex,
	QRect,
	QItemSelectionModel
)
from PyQt5.QtGui import (
	QStandardItemModel
)
from PyQt5.QtWidgets import (
	QApplication,
	QDesktopWidget,
	QVBoxLayout,
	QPushButton,
	QWidget,
	QTableWidget,
	QLineEdit,
	QTableWidgetItem,
	QTableWidgetSelectionRange
)

from runcsv import *

# Priorities:
# TODO ASAP: Save file and Open file
# TODO: Fancy selection using "Shift"
# TODO: Quality of life:
#	- Tab button has to be fixed someday


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

		# Table
		self.tableWidget = QTableWidget(self)
		self.tableWidget.setRowCount(nbRows)
		self.tableWidget.setColumnCount(nbCols)
		self.tableWidget.setHorizontalHeaderLabels([str(i) for i in range(nbRows)])
		self.tableWidget.setVerticalHeaderLabels([str(i) for i in range(nbCols)])
		self.tableWidget.itemSelectionChanged.connect(self.onCellChanged)

		# Formula editor
		self.formulaEdit = FormulaEdit(self, self)
		self.formulaEdit.textChanged.connect(self.onFormulaChange)
		self.formulaEdit.returnPressed.connect(self.formulaReturnPress)


		# Run button
		self.runBtn = QPushButton("Run")
		self.runBtn.clicked.connect(self.runSheet)

		# Create a QHBoxLayout instance
		layout = QVBoxLayout()
		# Add widgets to the layout
		layout.addWidget(self.formulaEdit)
		layout.addWidget(self.tableWidget)
		layout.addWidget(self.runBtn, 2)
		# Set the layout on the application's window
		self.setLayout(layout)
	
	def onCellChanged(self):
		# TODO: There should be a way to press Escape and return back to where we were
		self.affectCell(self.ci, self.cj) # Maybe not the most efficient way to do it
		self.ci = self.tableWidget.currentRow()
		self.cj = self.tableWidget.currentColumn()
		if len(self.tableWidget.selectedItems()) > 1:
			self.formulaEdit.clearFocus()
		else:
			self.formulaEdit.setFocus()
			self.formulaEdit.setText(s[self.ci][self.cj])
		print(self.ci,self.cj)
	
	def onFormulaChange(self):
		s[self.ci][self.cj] = self.formulaEdit.text()
	
	def down(self):
		if(self.ci!=nbRows-1):
			self.tableWidget.setCurrentCell(self.ci+1,self.cj)

	def up(self):
		if(self.ci!=0):
			self.tableWidget.setCurrentCell(self.ci-1,self.cj)

	def right(self):
		if(self.cj!=nbCols-1):
			self.tableWidget.setCurrentCell(self.ci,self.cj+1)

	def left(self):
		if(self.cj!=0):
			self.tableWidget.setCurrentCell(self.ci,self.cj-1)

	def formulaReturnPress(self, key=None):
		self.down()
	
	def runSheet(self):
		for i in np.arange(s.shape[0]):
			for j in np.arange(s.shape[1]):
				self.affectCell(i,j)
	
	def affectCell(self,i,j):
		try:
			process_cell(i,j)
			newitem = QTableWidgetItem(f[i][j])
			self.tableWidget.setItem(i,j, newitem)
		except:
			print("There was an error in cell {"+str(i)+","+str(j)+"}")

	def keyPressEvent(self, event):
		key = event.key()
		if(key == Qt.Key_Delete):
			for modelIndex in self.tableWidget.selectedIndexes():
				row = modelIndex.row()
				column = modelIndex.column()
				s[row][column] = ""
				self.affectCell(row,column)
		QWidget.keyPressEvent(self,event)

# TODO: Add Tab function

class FormulaEdit(QLineEdit):
	def __init__(self, editor : MainWindow, parent):
		QLineEdit.__init__(self, parent)
		self.editor = editor
	
	def keyPressEvent(self, event):
		key = event.key()
		if key == Qt.Key_Up:
			self.editor.up()
		elif key == Qt.Key_Down:
			self.editor.down()
		elif key == Qt.Key_Left and self.editor.formulaEdit.cursorPosition() == 0:
			self.editor.left()
		elif key == Qt.Key_Right and self.editor.formulaEdit.cursorPosition() == len(self.editor.formulaEdit.text()):
			self.editor.right()
		QLineEdit.keyPressEvent(self, event)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())

