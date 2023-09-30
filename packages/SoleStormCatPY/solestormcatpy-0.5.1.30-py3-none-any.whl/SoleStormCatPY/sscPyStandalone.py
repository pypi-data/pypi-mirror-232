"""This is the standalone app for 'SoleStormCatPY'. Here, any user can use 'SoleStormCatPY' with little to no coding (Depends on if the user uses a script to open this script). Here is how you can make your own script to open this app:

import SoleStormCatPY.sscPyStandalone as SSCstand

SSCstand.fullPythonApp()
"""

from tkinter import *
from tkinter.ttk import *
from time import strftime

"Apps"
def WebGUI():
	import SoleStormCatPY.WebOpen
	SoleStormCatPY.WebOpen.webGUI()
def TerminalGUI():
	import SoleStormCatPY.terminal
	SoleStormCatPY.terminal.terminalGUI()
def SystemInfo():
	import SoleStormCatPY.SystemInfo as si
	si.systemInfoPrint(deviceOS,userName,pythonVersion)
def ClockTimerGUI():
	import SoleStormCatPY.ClockTimer
	SoleStormCatPY.ClockTimer.clockTimerGUI()
def FilesGUI():
	import SoleStormCatPY.files
	files.filesGUI()

def SoleStormCatUpdate():
	UpgradeFrame = Tk()
	UpgradeFrame.title('SoleStormCatPY - Update')
	UpgradeFrame.geometry('50x1000')
	
	UpgradeLabel = Label(UpgradeFrame, text='SoleStormCatPY is currently being upgraded to the latest version. You may view progress in terminal.')
	UpgradeLabel.pack()
	
	os.system('pip install --upgrade SoleStormCatPY')
	
	UpgradeLabel.mainloop()
	
"App Loader:"
def fullPythonApp():
	frame = Tk()
	frame.title('SoleStormCatPY')
	frame.geometry('1024x768')
	
	MenuBar = Menu(frame)
	file = Menu(MenuBar, tearoff=0)
	MenuBar.add_cascade(label ="File", menu = file)
	file.add_command(label ="Update", command=SoleStormCatUpdate)
	file.add_command(label ="Quit", command=quit)
	
	appsBar = Menu(MenuBar, tearoff=0)
	MenuBar.add_cascade(label ="Apps", menu = appsBar)
	appsBar.add_command(label ="ClockTimer", command=ClockTimerGUI)
	appsBar.add_command(label ="System Info", command=SystemInfo)
	appsBar.add_command(label ="Terminal", command=TerminalGUI)
	appsBar.add_command(label ="Web", command=WebGUI)
	appsBar.add_command(label ="Files", command=FilesGUI)
	
	"GUI TAB"
	appLabel = Label(frame, text = 'Welcome to "SoleStormCatPY"! Please choose an app below!')
	appLabel.pack()
	
		
	WebB = Button(frame,text='Web', command=lambda: WebGUI())
	WebB.pack()
	
	
	TerminalB = Button(frame,text='Terminal', command=lambda: TerminalGUI())
	TerminalB.pack()
	
	
	SystemInfoB = Button(frame,text='System Info', command=lambda: SystemInfo())
	SystemInfoB.pack()
	
		
	ClockTimerB = Button(frame,text='ClockTimer', command=lambda: ClockTimerGUI())
	ClockTimerB.pack()
	
	FilesGUIB = Button(frame,text='Files', command=lambda: FilesGUI())
	FilesGUIB.pack()

	
	frame.config(menu = MenuBar)
	frame.mainloop()
