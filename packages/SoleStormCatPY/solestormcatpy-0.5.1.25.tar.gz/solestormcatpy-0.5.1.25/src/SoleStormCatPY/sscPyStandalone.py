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
	

"For TERMINAL apps"
import SoleStormCatPY.GreeNotes as GN
import SoleStormCatPY.files
	
"App Loader:"
def fullPythonApp():
	frame = Tk()
	frame.title('SoleStormCatPY')
	frame.geometry('1024x768')
	
	tabControl = Notebook(frame)

	tabGUI = Frame(tabControl)
	tabCMD = Frame(tabControl)
	tabControl.add(tabGUI, text="GUI Apps")
	tabControl.add(tabCMD, text="Terminal Apps")
	tabControl.pack(expand=1, fill="both")
	
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
	
	CMDappsBar = Menu(MenuBar, tearoff=0)
	MenuBar.add_cascade(label ="Apps (Terminal)", menu = CMDappsBar)
	CMDappsBar.add_command(label ="GreeNotes (Terminal)", command=GN.GreeNotes())
	CMDappsBar.add_command(label ="Files (Terminal)", command=SoleStormCatPY.files.filesCMD())
	
	"GUI TAB"
	appLabel = Label(tabGUI, text = 'Welcome to "SoleStormCatPY"! Please choose an app below!')
	appLabel.pack()
	
		
	WebB = Button(tabGUI,text='Web', command=lambda: WebGUI())
	WebB.pack()
	
	
	TerminalB = Button(tabGUI,text='Terminal', command=lambda: TerminalGUI())
	TerminalB.pack()
	
	
	SystemInfoB = Button(tabGUI,text='System Info', command=lambda: SystemInfo())
	SystemInfoB.pack()
	
		
	ClockTimerB = Button(tabGUI,text='ClockTimer', command=lambda: ClockTimerGUI())
	ClockTimerB.pack()
	
	FilesGUIB = Button(tabGUI,text='Files', command=lambda: FilesGUI())
	FilesGUIB.pack()
	
	"TERMINAL TAB"
	appLabel = Label(tabCMD, text = 'Welcome to "SoleStormCatPY"! Please choose an app below! (Terminal Apps)')
	appLabel.pack()
	
	GreeNotesB = Button(tabCMD,text="GreeNotes (Terminal)", command=lambda: GN.GreeNotes())
	GreeNotesB.pack()
	
	FilesB = Button(tabCMD,text="Files (Terminal)", command=lambda: SoleStormCatPY.files.filesCMD())
	FilesB.pack()
	
	frame.config(menu = MenuBar)
	frame.mainloop()

