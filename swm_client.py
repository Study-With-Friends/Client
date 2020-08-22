import os
import win32file
import win32con
from tkinter import filedialog
from tkinter import *
import requests

ACTIONS = {
    1 : "Created",
    2 : "Deleted",
    3 : "Modified",
    4 : "Renamed from",
    5 : "to"
}
FILE_LIST_DIRECTORY = 0x0001
URL = "https://3affc17a5073.ngrok.io/v1/files/upload"

def getWorkingDir():
    root = Tk()
    root.withdraw()
    selectedDir = filedialog.askdirectory(initialdir=os.getcwd())
    return selectedDir

def getCredentials(cwd):
    f = open(os.path.join(cwd, ".swm"), "r")
    email = f.readline().strip()
    password = f.readline().strip()
    return email, password

def uploadFile(cwd, filePath):
    email, password = getCredentials(cwd)
    dataObj = {
        "email": email,
        "password": password,
        "fileId": os.path.getctime(filePath)
    }
    print("Sending file", filePath)
    print("'" + email + "'" + password + "'")
    ret = requests.post(URL, data=dataObj, files={
        "file": open(filePath,'rb')
    })
    print(ret.text)

def workloop(cwd):
    print("Running SWM client in " + cwd)
    dirHandle = win32file.CreateFile(
                          cwd, 
                          FILE_LIST_DIRECTORY,
                          win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                          None, 
                          win32con.OPEN_EXISTING,
                          win32con.FILE_FLAG_BACKUP_SEMANTICS,
                          None)

    while 1:
        results = win32file.ReadDirectoryChangesW(
                            dirHandle,
                            4096,
                            True,
                            win32con.FILE_NOTIFY_CHANGE_FILE_NAME  |
                            win32con.FILE_NOTIFY_CHANGE_DIR_NAME   |
                            win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                            win32con.FILE_NOTIFY_CHANGE_SIZE       |
                            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                            win32con.FILE_NOTIFY_CHANGE_SECURITY,
                            None,
                            None)
        for action, file in results:
            filePath = os.path.join(cwd, file)
            print(ACTIONS.get(action, "Unknown"), filePath)
            uploadFile(cwd, filePath)

def main():
    dir = getWorkingDir()
    workloop(dir)

if __name__ == "__main__":
    main()
