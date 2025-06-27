#!/usr/bin/env python3
# To convert existing indentation from spaces to tabs hit Ctrl+Shift+P and type:
# Convert indentation to Tabs
import getJProtectToken #getJProtectToken.py
import exportAlertData #exportAlertData.py
import requests #not sure if needed here or only sub-files?
import sys
import json #not sure if needed here or only in sub-files?
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QCheckBox,
							 QLabel, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit,
							QStackedWidget, QTextEdit, QTreeWidget, QTreeWidgetItem)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

accessToken=""

class MainWindow(QMainWindow):
	def __init__(self):#constructor of my mainwindow
		super().__init__()
		self.setGeometry(700, 300, 500, 500)

		self.stack = QStackedWidget()
		self.setCentralWidget(self.stack)

		self.loginPage = self.createLoginPage()
		self.optionsPage = self.createOptionsPage()

		self.stack.addWidget(self.loginPage)    # index 0
		self.stack.addWidget(self.optionsPage)  # index 1

		self.stack.setCurrentIndex(0)           # 👈 show login page by default

	
	def createLoginPage(self):#initial the user interface
		loginPageWidget = QWidget()
	
		self.saveCredentialsCheckbox = QCheckBox("Save credentials", self)#can use a layout manager to replace self, but self is simpler for now
		#self.saveCredentialsCheckbox.stateChanged.connect(self.checkbox_changed)
		self.authenticateButton = QPushButton("Authenticate", self)
		self.hostnameBox = QLineEdit(self) #this is just a text box, called something silly for some reason
		self.apiClientBox = QLineEdit(self) #The order of these matters
		self.clientSecretBox = QLineEdit(self) #the first box listed is the one your cursor will default to
		

		self.authenticateButton.setGeometry(0, 0, 200, 200)
		self.authenticateButton.setStyleSheet("font-size: 30px;")
		#this is called connecting a signal to a slot? It makes the button functio do something
		self.authenticateButton.clicked.connect(self.clickedAuthenticate)#the 'connect' is the signal and 'self.clickedAuthenticate' is the slot

		self.saveCredentialsCheckbox.setChecked(False)#could set to True if want it checked by default

		self.hostnameBox.setPlaceholderText("Hostname")
		self.apiClientBox.setPlaceholderText("API Client")
		self.clientSecretBox.setPlaceholderText("Client Secret")
		
		grid = QGridLayout()#using the grid layout
		grid.addWidget(self.hostnameBox, 0, 0)
		grid.addWidget(self.apiClientBox, 1, 0)
		grid.addWidget(self.clientSecretBox, 2, 0)
		grid.addWidget(self.saveCredentialsCheckbox, 3, 0)
		grid.addWidget(self.authenticateButton, 4, 0)
		
		loginPageWidget.setLayout(grid)

		return loginPageWidget

	def createOptionsPage(self):
		optionsPageWidget = QWidget()
		
  		#do stuff
		self.label = QLabel("🎉 Login Successful!")

		#makes our options tree
		# ———————————————————————————————————————
		self.tree = QTreeWidget()
		self.tree.setHeaderHidden(True)  # Hide column headers

		# --- Reports Section ---Qt.ItemFlag.ItemIsTristate
		self.reports = QTreeWidgetItem(["Reports"])
		self.reports.setFlags(self.reports.flags() | Qt.ItemFlag.ItemIsUserCheckable)

		self.exportAlertDataCheckbox = QTreeWidgetItem(["Export Alert Data"])
		self.exportAlertDataCheckbox.setCheckState(0, Qt.CheckState.Unchecked)

		self.script2 = QTreeWidgetItem(["Script 2"])
		self.script2.setCheckState(0, Qt.CheckState.Unchecked)

		self.reports.addChildren([self.exportAlertDataCheckbox, self.script2])

		# --- Cleanup Section ---
		self.cleanup = QTreeWidgetItem(["Cleanup"])
		self.cleanup.setFlags(self.cleanup.flags() | Qt.ItemFlag.ItemIsUserCheckable)

		self.unused_computers = QTreeWidgetItem(["Unused Computers"])
		self.unused_computers.setCheckState(0, Qt.CheckState.Unchecked)

		self.unused_alerts = QTreeWidgetItem(["Unused Alerts"])
		self.unused_alerts.setCheckState(0, Qt.CheckState.Unchecked)

		self.cleanup.addChildren([self.unused_computers, self.unused_alerts])

		# Add sections to tree
		self.tree.addTopLevelItems([self.reports, self.cleanup])
		self.tree.setFixedSize(200,200)#sets the size of our option tree
		# ———————————————————————————————————————
  
		#makes our button
		self.runButton = QPushButton("Run Actions", self)
		self.runButton.setGeometry(0, 0, 200, 200)
		self.runButton.setStyleSheet("font-size: 30px;")
		self.runButton.clicked.connect(self.clickedRun)#the 'connect' is the signal and 'self.clickedAuthenticate' is the slot
  
		#makes our box to put information to
		self.outputBox = QTextEdit()
		self.outputBox.setReadOnly(True)

		#makes/sets our grid layout
		grid = QGridLayout()#using the grid layout
		grid.addWidget(self.tree, 0, 0)#add our option tree
		grid.addWidget(self.runButton, 1, 0)
		grid.addWidget(self.outputBox, 2, 0)
		optionsPageWidget.setLayout(grid)
  
		return optionsPageWidget
	
	def clickedAuthenticate(self):
		print("Button Clicked")

		#Get text from the text box, input into local variable
		hostname = self.hostnameBox.text()
		apiClient = self.apiClientBox.text()
		clientSecret = self.clientSecretBox.text()
		
		#just for troubleshooting
		print(f"hostanme is: {hostname}")
		print(f"Client: {apiClient}")
		print(f"Secret: {clientSecret}")
		
		#getAccessToken(serverURL, clientID, clientSecret)
		global accessToken
		accessToken = getJProtectToken.getAccessToken(hostname, apiClient, clientSecret)

		if self.saveCredentialsCheckbox.isChecked() == 2:
			print("Saving Credentials with KeyRing")

		self.stack.setCurrentIndex(1)

	def clickedRun(self):
		print("clicked run")
		if self.exportAlertDataCheckbox.checkState(0) == Qt.CheckState.Checked:
			print("Alerts Export checkbox selected")
			exportAlertData.exportAlertData(accessToken, "ganderson")

		#do stuff
"""		
	def checkbox_changed(self, state):#the state value will be 0 for unchecked and 2 for checked
		print(Qt.CheckState.Checked)
		if state == self.checkbox1.isChecked():#works with 2 but doesn't with any of the other built in options?
			self.label5.setText("YOU CHECKED THE BOX")
		else:
			self.label5.setText("YOU don't like food?")
"""

def main():
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec()) #this make it wait around for input

if __name__== "__main__":
	main()