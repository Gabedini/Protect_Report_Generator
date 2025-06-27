#!/usr/bin/env python3

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QCheckBox,
                             QLabel, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class MainWindow(QMainWindow):
	def __init__(self):#constructor of my mainwindow
		super().__init__()
		self.setGeometry(700, 300, 500, 500)
		self.label1 = QLabel("#1", self)#setting 'self.' to start, makes it fall under the class 'MainWindow' instead of the function 'initUI'
		self.checkbox1 = QCheckBox("Do you like food?", self)#can use a layout manager to replace self, but self is simpler for now
		self.label3 = QLabel("#3", self)
		self.label4 = QLabel("#4", self)
		self.label5 = QLabel("#5", self)
		self. button = QPushButton("Click Me!", self)
		self.line_edit = QLineEdit(self) #this is just a text box, called something silly for some reason
		self.initUI()

		"""self.setWindowTitle("Protect Report Generator")
		self.setGeometry(900, 600, 500, 500) #position on screen - 4 options: position x,position y,width,height
		self.setWindowIcon(QIcon("PRG_icon.png")) #this does nothing on macOS lol

		label = QLabel("Hello", self) #self is the window object we're calling
		label.setFont(QFont("Arial", 30)) #fontname, font size
		label.setGeometry(300,200,300,100) #I'm not 100% how this works, need to look up what that means
		label.setStyleSheet("color: #2596be;"#can pass css values, so rbg or hex works here
							"background-color: 2a7136;" #doesn't seem to work? I think system color scheme is overridng
							"font-weight: bold;")
		
		label.setAlignment(Qt.AlignmentFlag.AlignCenter) #aligns text to center (veritcally)
		label.setAlignment(Qt.AlignmentFlag.AlignHCenter) #this appears to not work but I think it's centered in the label...problem is that the label isn't aligned due to above config
		#label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignLeft) #we can do more than one at once

		label = QLabel(self)
		label.setGeometry(0, 0, 250, 250)#x,y,width,heighth

		pixmapItem = QPixmap("PRG_icon.png")#makes pixmax object
		label.setPixmap(pixmapItem)#sets pixmax to a label

		label.setScaledContents(True)#makes pixmap object fit space given
		label.setGeometry(0, 0, label.width(), label.height())#x,y,width,heighth

		label.setGeometry(self.width() - label.width(), 0, 250, 250)#a way of right-justifying the image regardless of window size
		label.setGeometry((self.width() - label.width()) // 2, 0, 250, 250)#center justify... // 2 is integer division since no partial pixels
	"""
	
	def initUI(self):#initial the user interface
		central_widget = QWidget()
		self.setCentralWidget(central_widget)


		self.button.setGeometry(0, 0, 200, 200)
		self.button.setStyleSheet("font-size: 30px;")
		#this is called connecting a signal to a slot? It makes the button functio do something
		self.button.clicked.connect(self.on_click)#the 'connect' is the signal and 'self.on_click' is the slot

		self.label1.setStyleSheet("background-color: red;")
		self.checkbox1.setStyleSheet("background-color: purple;"
							   		"font-size: 30px;"
							   		"font-family: Helvetica;")
		self.checkbox1.setChecked(False)#could set to True if want it checked by default
		#just like the button, self.checkbox1.*signal*.connect(*slot)
		self.checkbox1.stateChanged.connect(self.checkbox_changed)

		self.label3.setStyleSheet("background-color: blue;")
		self.label4.setStyleSheet("background-color: green;")
		self.label5.setStyleSheet("background-color: yellow;"
									"color: black;")
		
		#just like the otheres, setting style sheet for the text box
		self.line_edit.setGeometry(10,20,200,60)#I think the grid is making this not work, but leaving for reference
		self.line_edit.setStyleSheet("font-size: 25px;"
							   "font-family: Times New Roman")
		self.line_edit.setPlaceholderText("Placeholdertext Here")


		"""vbox = QVBoxLayout()#vertical layout manager. Use QHBoxLayout for horizontal management
		vbox.addWidget(label1)
		vbox.addWidget(label2)
		vbox.addWidget(label3)
		vbox.addWidget(label4)
		vbox.addWidget(label5)
		
		central_widget.setLayout(vbox)"""

		grid = QGridLayout()#using the grid layout
		grid.addWidget(self.label1, 0, 0)
		grid.addWidget(self.checkbox1, 0, 1)
		grid.addWidget(self.label3, 1, 0)
		grid.addWidget(self.line_edit, 1, 1)
		#grid.addWidget(self.label4, 1, 1)
		grid.addWidget(self.label5, 1, 2)
		grid.addWidget(self.button, 0, 2)
		
		central_widget.setLayout(grid)


	def on_click(self):
		print("Button Clicked")
		self.button.setText("clicked!")#changes the button text after it's clicked
		self.button.setDisabled(True)#Greys out the button (after being clicked since in on_click function)

		self.label1.setText("Yay!!!!")

		#Get text from the text box, input into local variable
		textboxText = self.line_edit.text()
		print(f"Hello {textboxText}")

	def checkbox_changed(self, state):#the state value will be 0 for unchecked and 2 for checked
		print(Qt.CheckState.Checked)
		if state == self.checkbox1.isChecked():#works with 2 but doesn't with any of the other built in options?
			self.label5.setText("YOU CHECKED THE BOX")
		else:
			self.label5.setText("YOU don't like food?")

def main():
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec()) #this make it wait around for input

if __name__== "__main__":
	main()