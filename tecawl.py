import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import os
import functools
#import subprocess

class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
    
    def setColorScheme(self, hex):
        self.configure(bg=hex , font=("Padauk Book", 10), bd=0, highlightthickness=0, relief='ridge')

    def _proxy(self, *args):
        # let the actual widget perform the requested action
        cmd = (self._orig,) + args
        result = self.tk.call(cmd)

        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (args[0] in ("insert", "replace", "delete") or 
            args[0:3] == ("mark", "set", "insert") or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")

        # return what the actual widget returned
        return result     


class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        #change color of textbox#change color of textbox
        self.textwidget = None

    def setColorScheme(self, hex):
        self.configure(bg=hex, bd=0, highlightthickness=0, relief='ridge')

    def attach(self, text_widget):
        self.textwidget = text_widget
        # secret font=("Redacted Script", 10)

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2,y,anchor="nw", text=linenum)
            i = self.textwidget.index("%s+1line" % i)
    
def checkContents(*args):
    ind = myNotebook.index(myNotebook.select())
    if ind != 0:
        lineList[ind-1].redraw()

def shiftDownTab(*args):
    try:
        ind = myNotebook.index(myNotebook.select())
        #set focus
        myNotebook.select(ind - 1)
    except:
        return

def shiftUpTab(*args):
    try:
        ind = myNotebook.index(myNotebook.select())
        #set focus
        myNotebook.select(ind + 1)
    except:
        return

def deleteTab(*args):
    ind = myNotebook.index(myNotebook.select()) - 1
    print(ind)
    tabList.pop(ind)
    lineList.pop(ind)
    txtList.pop(ind)
    myNotebook.forget(myNotebook.select())

def configureGrid():
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)
 
    myNotebook.rowconfigure(0, weight=1)
    myNotebook.columnconfigure(0, weight=1)

    helpFrame.rowconfigure(0, weight=1)
    helpFrame.columnconfigure(0, weight=1)
    helpFrame.columnconfigure(1, weight=1)
    helpFrame.columnconfigure(2, weight=1)

    schemeFrame.rowconfigure(0, weight=1)
    schemeFrame.rowconfigure(1, weight=1)
    schemeFrame.rowconfigure(2, weight=1)
    schemeFrame.rowconfigure(3, weight=1)
    schemeFrame.rowconfigure(4, weight=1)
    schemeFrame.columnconfigure(0, weight=1)

    keyBindings.rowconfigure(0, weight=1)
    keyBindings.rowconfigure(1, weight=1)
    keyBindings.rowconfigure(2, weight=1)
    keyBindings.rowconfigure(3, weight=1)
    keyBindings.rowconfigure(4, weight=1)
    keyBindings.columnconfigure(0, weight=1)


def newTab(*args):
    #get screen position
    screenPosx = window.winfo_x()
    screenPosy = window.winfo_y()

    #create popup window
    popup = tk.Tk()
    popup.configure(bg="black")
    popup.title("Create Window")
    popup.geometry('175x25+{}+{}'.format(screenPosx, screenPosy))
    popup.resizable(width=False, height=False)

    #create entry and button - when button pressed create tab and close popup
    fileName = tk.Entry(popup, bg=keyBindings["foreground"])
    fileName.focus_set()
    fileName.pack(fill="both", padx=5, pady=2)
    fileName.bind("<Return>", lambda ev: createTab(popup, fileName.get()))

def createTab(popup, fileName):
    global lineList

    f = open(fileName,"w")
    f.close()

    #add new tab
    newFileTab = tk.Frame(myNotebook, bg="black")
    myNotebook.add(newFileTab, text=fileName)

    #close window
    popup.destroy()
    
    #create code textbox
    codeTxt = CustomText(newFileTab, padx=5)
    CustomText.setColorScheme(codeTxt, myPurple)
    txtList.append(codeTxt)

    #create line number object
    lineNum = TextLineNumbers(newFileTab, height=40, width=30)
    TextLineNumbers.setColorScheme(lineNum, myLightPurple)
    lineNum.attach(codeTxt)
    lineList.append(lineNum)

    #configure window
    newFileTab.rowconfigure(0, weight=1)
    newFileTab.columnconfigure(0, weight=1)
    newFileTab.columnconfigure(1, weight=30)

    #set widgets to grid
    lineNum.grid(row=0, column=0, sticky="ns")
    codeTxt.grid(row=0, column=1, sticky="nsew") 

    codeTxt.bind('<Tab>', tabKeyPress)
    codeTxt.bind("<<Change>>", checkContents)
    codeTxt.bind("<Configure>", checkContents)
    codeTxt.bind("<Control-s>", lambda ev: saveFile(ev, input=codeTxt.get("1.0",'end-1c')))

    #set focus
    myNotebook.select(newFileTab)

def saveFile(ev, input):
    fileName = myNotebook.tab(myNotebook.select(), "text")
    f = open(fileName, "w")
    f.write(input)
    f.close()


def tabKeyPress(ev, codeTxt):
    codeTxt.insert(tk.INSERT,"    ")
    return 'break'

def returnKeyPress(ev, codeTxt):

    input = codeTxt.get("insert linestart", "insert lineend") 
    if len(input) < 4:
        return

    first4 = input[:4]
    tabStop = ""
    last=input[-1]

    if first4 == "    ":
        tabStop = "    "

    if first4 == "    ":
        codeTxt.insert(tk.INSERT,"\n{x}".format(x=tabStop))
        return 'break'
    if last == "{" or ":":
        codeTxt.insert(tk.INSERT,"\n    {x}".format(x=tabStop))
        return 'break'

def changeToOrange(*args):
    style.theme_use("oran")
    schemeFrame.configure(fg=myOrange)
    keyBindings.configure(fg=myOrange)
    for txt in txtList:
        CustomText.setColorScheme(txt, myOrange)
    for line in lineList:
        TextLineNumbers.setColorScheme(line, myLightOrange)
    for lbl in binds:
        lbl.configure(fg=myOrange)

def changeToPink(*args):
    style.theme_use("pin")
    schemeFrame.configure(fg=myPink)
    keyBindings.configure(fg=myPink)
    for txt in txtList:
        CustomText.setColorScheme(txt, myPink)
    for line in lineList:
        TextLineNumbers.setColorScheme(line, myLightPink)
    for lbl in binds:
        lbl.configure(fg=myPink)

def changeToBlue(*args):
    style.theme_use("blu")
    schemeFrame.configure(fg=myBlue)
    keyBindings.configure(fg=myBlue)
    for txt in txtList:
        CustomText.setColorScheme(txt, myBlue)
    for line in lineList:
        TextLineNumbers.setColorScheme(line, myLightBlue)
    for lbl in binds:
        lbl.configure(fg=myBlue)

def changeToGreen(*args):
    style.theme_use("gree")
    schemeFrame.configure(fg=myGreen)
    keyBindings.configure(fg=myGreen)
    for txt in txtList:
        CustomText.setColorScheme(txt, myGreen)
    for line in lineList:
        TextLineNumbers.setColorScheme(line, myLightGreen)
    for lbl in binds:
        lbl.configure(fg=myGreen)

def changeToPurple(*args):
    style.theme_use("purp")
    schemeFrame.configure(fg=myPurple)
    keyBindings.configure(fg=myPurple)
    for txt in txtList:
        CustomText.setColorScheme(txt, myPurple)
    for line in lineList:
        TextLineNumbers.setColorScheme(line, myLightPurple)
    for lbl in binds:
        lbl.configure(fg=myPurple)

#create window
window = tk.Tk()
window.title('Tecawl')
window.configure(bg="black")

#create styles for colorscheme
myPurple = "#7A2BF5"
myLightPurple = "#8A6FB2"
myBlue = "#498FAD"
myLightBlue = "#82A5B4" 
myOrange = "#977933"
myLightOrange = "#BCA46D"
myGreen = "#05B479"
myLightGreen = "#7FD3B7"
myPink = "#973356"
myLightPink = "#C66F88"

style = ttk.Style()
style.theme_create( "purp", parent="alt", settings={
        "TNotebook": {"configure": {"borderwidth" : 0, "tabposition": "ws", "background": "black"}},
        "TNotebook.Tab": {
            "configure": {"padding": [5, 1], "background": "black", "foreground": myPurple},
            "map":       {"background": [("selected", myPurple)],"foreground": [("selected", "black")],
                          "expand": [("selected", [1, 1, 1, 0])] } } } )
style = ttk.Style()
style.theme_create( "blu", parent="alt", settings={
        "TNotebook": {"configure": {"borderwidth" : 0, "tabposition": "ws", "background": "black"}},
        "TNotebook.Tab": {
            "configure": {"padding": [5, 1], "background": "black", "foreground": myBlue},
            "map":       {"background": [("selected", myBlue)],"foreground": [("selected", "black")],
                        "expand": [("selected", [1, 1, 1, 0])] } } } )
style = ttk.Style()
style.theme_create( "oran", parent="alt", settings={
        "TNotebook": {"configure": {"borderwidth" : 0, "tabposition": "ws", "background": "black"}},
        "TNotebook.Tab": {
            "configure": {"padding": [5, 1], "background": "black", "foreground": myOrange},
            "map":       {"background": [("selected", myOrange)],"foreground": [("selected", "black")],
                        "expand": [("selected", [1, 1, 1, 0])] } } } )
style = ttk.Style()
style.theme_create( "gree", parent="alt", settings={
        "TNotebook": {"configure": {"borderwidth" : 0, "tabposition": "ws", "background": "black"}},
        "TNotebook.Tab": {
            "configure": {"padding": [5, 1], "background": "black", "foreground": myGreen},
            "map":       {"background": [("selected", myGreen)],"foreground": [("selected", "black")],
                        "expand": [("selected", [1, 1, 1, 0])] } } } )

style = ttk.Style()
style.theme_create( "pin", parent="alt", settings={
        "TNotebook": {"configure": {"borderwidth" : 0, "tabposition": "ws", "background": "black"}},
        "TNotebook.Tab": { 
            "configure": {"padding": [5, 1], "background": "black", "foreground": myPink},
            "map":       {"background": [("selected", myPink)],"foreground": [("selected", "black")],
                          "expand": [("selected", [1, 1, 1, 0])] } } } )

style.theme_use("purp")

#create tabs
style.configure('lefttab.TNotebook', tabposition='ws')
myNotebook = ttk.Notebook(window, style='lefttab.TNotebook')
myNotebook.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

#add help tab
helpFrame = tk.Frame(myNotebook, bg="black")
myNotebook.add(helpFrame, text="My Config")
schemeFrame = tk.LabelFrame(helpFrame, text="Mood", 
    bg="black", fg=myPurple)
schemeFrame.grid(row=0, column=0, sticky="nsew",padx=15, pady=15)
orange = tk.Button(schemeFrame, text="Orange", borderwidth=0, highlightthickness=0, 
    activebackground="black", bg="black", fg=myOrange, activeforeground=myOrange,
    command=lambda: changeToOrange())
orange.grid(row=0, column=0, sticky="nsew")
pink = tk.Button(schemeFrame, text="Pink", highlightthickness=0, activebackground="black",
    bg="black", fg=myPink,activeforeground=myPink,borderwidth=0,command=lambda: changeToPink())
pink.grid(row=1, column=0, sticky="nsew")
blue = tk.Button(schemeFrame, text="Blue", highlightthickness=0, bg="black", fg=myBlue,
    activebackground="black", activeforeground=myBlue, borderwidth=0,command=lambda: changeToBlue())
blue.grid(row=2, column=0, sticky="nsew")
green = tk.Button(schemeFrame, text="Green", highlightthickness=0, bg="black", fg=myGreen,
    activebackground="black", activeforeground=myGreen,borderwidth=0,command=lambda: changeToGreen())
green.grid(row=3, column=0, sticky="nsew")
purple = tk.Button(schemeFrame, text="Purple", highlightthickness=0, bg="black", fg=myPurple,
    activebackground="black", activeforeground=myPurple,borderwidth=0, command=lambda: changeToPurple())
purple.grid(row=4, column=0, sticky="nsew")

#add key bindings to help page
binds = []
keyBindings = tk.LabelFrame(helpFrame, text="Bindings", 
    bg="black", fg=myPurple)
keyBindings.grid(row=0, column=1, columnspan=2, sticky="nsew",padx=15, pady=15)
upTab = tk.Label(keyBindings, text="Control+UpArrow = Up Tab", highlightthickness=0, borderwidth=0, 
    bg="black", fg=myPurple)
upTab.grid(row=0, column=0, sticky="nsew")
binds.append(upTab)
downTab = tk.Label(keyBindings, text="Control+DownArrow = Down Tab", highlightthickness=0, borderwidth=0, 
    bg="black",fg=myPurple)
downTab.grid(row=1, column=0, sticky="nsew")
binds.append(downTab)
closeTab = tk.Label(keyBindings, text="Control+LeftArrow = Hide Tab", highlightthickness=0, borderwidth=0, 
    bg="black",fg=myPurple)
closeTab.grid(row=2, column=0, sticky="nsew")
binds.append(closeTab)
save = tk.Label(keyBindings, text="Control+s = Save File", highlightthickness=0, borderwidth=0, 
    bg="black", fg=myPurple)
save.grid(row=3, column=0, sticky="nsew")
binds.append(save)
makeFile = tk.Label(keyBindings, text="Control+m = Create file", highlightthickness=0, borderwidth=0, 
    bg="black", fg=myPurple)
makeFile.grid(row=4, column=0, sticky="nsew")
binds.append(makeFile)



#create label for filesystem
files = [f for f in os.listdir('.') if os.path.isfile(f) and f[-4:]!='.jpg']
i = 0

#hold tabs in array
global tabList 
tabList = []
global txtList 
txtList = []
global lineList
lineList = []

for f in files:
    tabList.append(tk.Frame(myNotebook, bg="black"))

count = 0
for f in files:
    myNotebook.add(tabList[count], text=f)   

    #create code textbox
    codeTxt = CustomText(tabList[count], padx=5)
    CustomText.setColorScheme(codeTxt, myPurple)
    txtList.append(codeTxt)

    #create line number object
    lineNum = TextLineNumbers(tabList[count], height=40, width=30)
    TextLineNumbers.setColorScheme(lineNum, myLightPurple)
    lineNum.attach(codeTxt)
    lineList.append(lineNum)

    tabList[count].rowconfigure(0, weight=1)
    tabList[count].columnconfigure(0, weight=1)
    tabList[count].columnconfigure(1, weight=30)

    #set widgets to grid
    lineNum.grid(row=0, column=0, sticky="nsew")
    codeTxt.grid(row=0, column=1, sticky="nsew") 

    #read file contents and display in text box
    writeFile = open(f,"r")
    txtList[count].insert(tk.END, writeFile.read())

    count += 1

for j in range(len(tabList)):
    #refresh line numbers
    lineList[j].redraw()


#configure the grid layout of app
configureGrid()

#write line numbers every enter key press
for j in range(len(tabList)):
    txtList[j].bind('<Tab>', lambda ev: tabKeyPress(ev, codeTxt=txtList[myNotebook.index(myNotebook.select())-1]))
    txtList[j].bind("<<Change>>", checkContents)
    txtList[j].bind("<Configure>", checkContents)
    txtList[j].bind("<Return>", lambda ev: returnKeyPress(ev, codeTxt=txtList[myNotebook.index(myNotebook.select())-1]))
    txtList[j].bind("<Control-s>", lambda ev: saveFile(ev, 
        input=txtList[myNotebook.index(myNotebook.select())-1].get("1.0",'end-1c')))

window.bind("<Control-m>", newTab)
window.bind("<Control-Up>", shiftDownTab)
window.bind("<Control-Down>", shiftUpTab)
window.bind('<Control-Left>', deleteTab)
    
window.mainloop()
