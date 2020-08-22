import os
from tkinter import filedialog
from tkinter import *
import requests
import platform
import time

ACTIONS = {
    1 : "Created",
    2 : "Deleted",
    3 : "Modified",
    4 : "Renamed from",
    5 : "Renamed to"
}
FILE_LIST_DIRECTORY = 0x0001
FILEID_FACTOR = 10000

URL = "http://6bdff97a9214.ngrok.io/v1/files/upload"
fileIds = {}

username = ""
password = ""

# class Client:

def getWorkingDir():
    root = Tk()
    root.withdraw()
    selectedDir = filedialog.askdirectory(initialdir=os.getcwd())
    return selectedDir

def getCredentials(cwd):
    try:
        f = open(os.path.join(cwd, ".swm"), "r")
        new_username = f.readline().strip()
        new_password = f.readline().strip()
        return new_username, new_password
    except:
        return None, None

def updateFile(action, fileId, filePath):
    dataObj = {
        "action": action,
        "username": username,
        "password": password,
        "fileId": fileId
    }
    print("Sending file", filePath, fileId, username, password)
    ret = requests.post(URL, data=dataObj, files={
        "file": open(filePath, 'rb')
    })
    print(ret.text)

def main():
    dir = getWorkingDir()
    if not dir:
        return
        
    username, password = getCredentials(dir)

    if not username or not password:
        print("No .swm file found in directory. Please create one with your username and password.")
        return
    else:
        print(username, password)

    print("Running SWM client in " + dir)
    if platform.system() == 'Windows':
        import swm_windows
        swm_windows.catalogueCurrentFiles(dir)
        swm_windows.workloop(dir)
    else:
        import swm_unix
        swm_unix.catalogueCurrentFiles(dir)
        w = swm_unix.Watcher(dir)
        w.run()

if __name__ == "__main__":
    main()
