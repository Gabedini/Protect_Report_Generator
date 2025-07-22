#!/usr/bin/env python3
# To convert existing indentation from spaces to tabs hit Ctrl+Shift+P and type:
# Convert indentation to Tabs

#importing other files:
import getJProtectToken, exportAlertData, deleteComputersFromCSV, generateComputerComplianceReport,generateDeviceControls, getAuditLogs
import requests #not sure if needed here or only sub-files?
import sys
import json #not sure if needed here or only in sub-files?
import keyring
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QCheckBox,
							 QLabel, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit,
							QStackedWidget, QTextEdit, QTreeWidget, QTreeWidgetItem, QComboBox)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

accessToken=""

class MainWindow(QMainWindow):
	def __init__(self):#constructor of my mainwindow
		super().__init__()
		self.setStyleSheet(self.load_stylesheet())
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
		
		#check if credentials were saved and autofill if they are needs to be added

  		#self.saveCredentialsCheckbox.stateChanged.connect(self.checkbox_changed)
		self.authenticateButton = QPushButton("Authenticate", self)
		self.hostnameBox = QLineEdit(self) #this is just a text box, called something silly for some reason
		self.apiClientBox = QLineEdit(self) #The order of these matters
		self.clientSecretBox = QLineEdit(self) #the first box listed is the one your cursor will default to
		self.clientSecretBox.setEchoMode(QLineEdit.EchoMode.Password)#obscuring the text from our secret
		

		self.authenticateButton.setGeometry(0, 0, 200, 200)
		self.authenticateButton.setStyleSheet("font-size: 30px;")
		#this is called connecting a signal to a slot? It makes the button functio do something
		self.authenticateButton.clicked.connect(self.clickedAuthenticate)#the 'connect' is the signal and 'self.clickedAuthenticate' is the slot

		#time to add logic to check if keyring items are stored in keychain
		#it would be ideal to check for all 3 as a failsafe but for now I think this is adequate
		if keyring.get_password("Jamf Protect Hostname", "Jamf Protect Hostname") != None:
			#sets save credentials to true, as that was selected previously
			self.saveCredentialsCheckbox.setChecked(True)
			#input saved credentials into the associated boxes.
			try:
				self.apiClientBox.setText(keyring.get_password("Protect API Client", "API Client"))
				self.clientSecretBox.setText(keyring.get_password("Protect Credentials", "Protect Credentials"))
				self.hostnameBox.setText(keyring.get_password("Jamf Protect Hostname", "Jamf Protect Hostname"))
			except keyring.errors.PasswordGetError:
				print("failed to retrieve password")
		else:
			#if it wasn't true previously, we keep it false
			self.saveCredentialsCheckbox.setChecked(False)

		self.hostnameBox.setPlaceholderText("Hostname")
		self.apiClientBox.setPlaceholderText("API Client")
		self.clientSecretBox.setPlaceholderText("Client Secret")
		
		grid = QGridLayout()#using the grid layout
		grid.setVerticalSpacing(12)       # ✅ Reduce space between rows
		grid.setHorizontalSpacing(10)     # (optional) fine-tune this too
		grid.setContentsMargins(0, 0, 0, 0)
		grid.addWidget(self.hostnameBox, 0, 0)
		grid.addWidget(self.apiClientBox, 1, 0)
		grid.addWidget(self.clientSecretBox, 2, 0)
		grid.addWidget(self.saveCredentialsCheckbox, 3, 0)
		grid.addWidget(self.authenticateButton, 4, 0)
  
		# Wrap grid in a centered container
		form_container = QWidget()
		form_container.setLayout(grid)
		form_container.setFixedWidth(300)  # ✅ Max width for form

		outer_layout = QVBoxLayout()
		outer_layout.addSpacing(60)  # Push form slightly down from top
		outer_layout.addWidget(form_container, alignment=Qt.AlignmentFlag.AlignHCenter)
		outer_layout.addStretch()  # ✅ Push content up from bottom

		loginPageWidget.setLayout(outer_layout)
		return loginPageWidget

	def createOptionsPage(self):
		optionsPageWidget = QWidget()
		
  		#do stuff
		self.label = QLabel("🎉 Login Successful!")

		#makes our options tree
		# ———————————————————————————————————————
		self.tree = QTreeWidget()
		self.tree.setHeaderHidden(True)  # Hide column headers

		# --- Reports Section --- Qt.ItemFlag.ItemIsTristate might be needed for some of these?
		self.reports = QTreeWidgetItem(["Reports"])
		self.reports.setFlags(self.reports.flags() | Qt.ItemFlag.ItemIsUserCheckable)
  
		# --- Reports Option 1: Export alerts to JSON ---
		self.exportAlertDataCheckbox = QTreeWidgetItem(["Export Alert Data"])
		self.exportAlertDataCheckbox.setCheckState(0, Qt.CheckState.Unchecked)

			# --- Option 1 sub-option 1: Alert Level Minimum Severity ---
		self.minSeverityItem = QTreeWidgetItem(self.exportAlertDataCheckbox)
		self.minSeverityCombo = QComboBox()
		self.minSeverityCombo.addItems(["Informational", "Low", "Medium", "High"])
		self.tree.setItemWidget(self.minSeverityItem, 0, self.minSeverityCombo)
			# --- Option 1 sub-option 2: Alert Level Maximum Severity ---
		self.maxSeverityItem = QTreeWidgetItem(self.exportAlertDataCheckbox)
		self.maxSeverityCombo = QComboBox()
		self.maxSeverityCombo.addItems(["Informational", "Low", "Medium", "High"])
		self.maxSeverityCombo.setCurrentText("High")  # setting default to high for the second box
		self.tree.setItemWidget(self.maxSeverityItem, 0, self.maxSeverityCombo)

  		# --- Reports Option 2: Generate Comliance Report ---
		self.generateComplianceReportCheckbox = QTreeWidgetItem(["Generate Computer Compliance Report"])
		self.generateComplianceReportCheckbox.setCheckState(0, Qt.CheckState.Unchecked)
  
		# --- Reports Option 3: Generate Device Controls ---
		self.generateDeviceControlsCheckbox = QTreeWidgetItem(["Generate Device Controls Report"])
		self.generateDeviceControlsCheckbox.setCheckState(0, Qt.CheckState.Unchecked)
  
			# --- Option 3 sub-option: Number of days selection ---
		self.numDaysItem = QTreeWidgetItem(self.generateDeviceControlsCheckbox)
		self.numDaysCombo = QComboBox()
		self.numDaysCombo.addItems([str(i) for i in range(1, 31)])#adds 1-30 to dropdown but in shorthand
		self.numDaysCombo.setCurrentText("30")  # sets default to 30
		self.tree.setItemWidget(self.numDaysItem, 0, self.numDaysCombo)
  
		# --- Reports Option 4: Audit Logs ---
		self.getAuditLogsCheckbox = QTreeWidgetItem(["Generate Jamf Protect Audit Logs"])
		self.getAuditLogsCheckbox.setCheckState(0, Qt.CheckState.Unchecked)
  
		# --- Adds checkboxes to reports section ---
		self.reports.addChildren([self.exportAlertDataCheckbox, self.generateComplianceReportCheckbox, self.generateDeviceControlsCheckbox, self.getAuditLogsCheckbox])


		# --- Cleanup Section ---
		self.cleanup = QTreeWidgetItem(["Cleanup"])
		self.cleanup.setFlags(self.cleanup.flags() | Qt.ItemFlag.ItemIsUserCheckable)

		# --- Cleanup Option 1: Delete Unused Computers"
		self.unused_computers = QTreeWidgetItem(["Unused Computers"])
		self.unused_computers.setCheckState(0, Qt.CheckState.Unchecked)
		# --- Cleanup Option 2: idk yet"
		self.unused_alerts = QTreeWidgetItem(["Unused Alerts"])
		self.unused_alerts.setCheckState(0, Qt.CheckState.Unchecked)

		self.cleanup.addChildren([self.unused_computers, self.unused_alerts])

		# Add sections to tree
		self.tree.addTopLevelItems([self.reports, self.cleanup])
		self.tree.setFixedSize(300,200)#sets the size of our option tree
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
	
	#this defines all of the logic for the login screen when the 'authenticate button is clicked
	def clickedAuthenticate(self):
		print("Button Clicked")

		#Get text from the text box, input into local variable
		hostname = self.hostnameBox.text()
		apiClient = self.apiClientBox.text()
		clientSecret = self.clientSecretBox.text()

		if self.saveCredentialsCheckbox.checkState() == Qt.CheckState.Checked:
			try:
				#create if doesn't exist/overwrites existing keyring items in case the user updates the value
				print("Saving login info with keyring")
				#saving api client to auto fill, saved securely to keychain even if not totally necessary
				keyring.set_password("Protect API Client", "API Client", apiClient)
				"""Here's saving the client secret to the Keychain, I'm naming it a little vague on purpose"""
				keyring.set_password("Protect Credentials", "Protect Credentials", clientSecret)
				"""And here we abuse keyring to save the URL as well as if it's a password
   						because I'm already using keyring, not because it makes sense to do this"""
				keyring.set_password("Jamf Protect Hostname", "Jamf Protect Hostname", hostname)
			except keyring.errors.PasswordSetError:
				print("failed to store password")
		else:
			#we should destroy the keyring items here if the user unchecks this box
			print("deleting keyring items, either they don't exist or they do and the box has been unchecked")
			#need to implement 'try' logic in more places I think
			try:
				keyring.delete_password("Protect API Client", "API Client")
				keyring.delete_password("Protect Credentials", "Protect Credentials")
				keyring.delete_password("Jamf Protect Hostname", "Jamf Protect Hostname")
			except keyring.errors.PasswordDeleteError:
				print("failed to delete password")

		#just for troubleshooting
		print(f"hostanme is: {hostname}")
		print(f"Client: {apiClient}")
		print(f"Secret: {clientSecret}")

		#getAccessToken(serverURL, clientID, clientSecret)
		global accessToken
		accessToken = getJProtectToken.getAccessToken(hostname, apiClient, clientSecret)
  
		#turns out we need the instance name sometimes so going to extract that from the URL:
		global instanceName #there are more elegant ways to do the below, meh
		splitProtocol=hostname.split('/')[2] #removes https (protocol) from URL
		instanceName=splitProtocol.split('.')[0] #splits anything after the instance name
		print(f"The instance name is: {instanceName}")

		if self.saveCredentialsCheckbox.isChecked() == 2:
			print("Saving Credentials with KeyRing")

		self.stack.setCurrentIndex(1)

	#thie function controls the logic for anything to run that is selected to run in the gui
	def clickedRun(self):
		print("clicked run")
		if self.exportAlertDataCheckbox.checkState(0) == Qt.CheckState.Checked:
			print("Alerts Export checkbox selected")
			minSeverity = self.minSeverityCombo.currentText()
			maxSeverity = self.maxSeverityCombo.currentText()
			print(f"Min/Max Severity Set: {minSeverity}:{maxSeverity}")
			exportAlertData.exportAlertData(accessToken, instanceName, minSeverity, maxSeverity)
			#add line to open file location. Output in window where file was saved
		if self.generateComplianceReportCheckbox.checkState(0) == Qt.CheckState.Checked:
			print("Generate Report checkbox selected")
			generateComputerComplianceReport.generateComputerComplianceReport(accessToken, instanceName)
   			#run compliance report script
			#also open file location? Ouptut in window where file was saved for sure though
		if self.generateDeviceControlsCheckbox.checkState(0) == Qt.CheckState.Checked:
			print("Generate Device Control checkbox selected")
			numDays = int(self.numDaysCombo.currentText())#have to convert to int
			generateDeviceControls.generateDeviceControls(accessToken, instanceName, numDays)
			#also open file location? Ouptut in window where file was saved for sure though
		if self.getAuditLogsCheckbox.checkState(0) == Qt.CheckState.Checked:
			print("Generate Audit Logs checkbox selected")
			getAuditLogs.getAuditLogs(accessToken, instanceName)
   			#run compliance report script
			#also open file location? Ouptut in window where file was saved for sure though

		#do stuff
  
	def load_stylesheet(self):
		return """
		QWidget {
			background-color: #1e1e1e;
			color: #f0f0f0;
			font-family: 'Segoe UI', sans-serif;
			font-size: 14px;
		}

		QLabel {
			font-weight: bold;
			color: #e0e0e0;
		}

		QLineEdit {
			background-color: #2c2c2c;
			border: 1px solid #444;
			border-radius: 5px;
			padding: 8px;
			color: #f0f0f0;
		}

		QLineEdit:focus {
			border: 1px solid #3fa46a;
		}

		QCheckBox {
			spacing: 6px;
			padding-left: 2px;
		}

		QTreeWidget {
			background-color: #2c2c2c;
			border: 1px solid #3fa46a;
			border-radius: 5px;
		}

		QTreeView::item {
			padding: 4px;
		}

		QTreeView::item:hover {
			background: #384038;
		}

		QTextEdit {
			background-color: #2c2c2c;
			border: 1px solid #444;
			border-radius: 5px;
			padding: 8px;
			color: #f0f0f0;
		}

		QPushButton {
			background-color: #3fa46a;
			color: white;
			font-weight: bold;
			padding: 10px;
			border-radius: 6px;
			font-size: 16px;
		}

		QPushButton:hover {
			background-color: #52c87a;
		}
		"""

def main():
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec()) #this make it wait around for input

if __name__== "__main__":
	main()