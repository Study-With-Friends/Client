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
    5 : "Renamed to"
}
FILE_LIST_DIRECTORY = 0x0001
URL = "http://6bdff97a9214.ngrok.io//v1/files/upload"
FILEID_FACTOR = 100000
fileIds = {}

def getWorkingDir():
    root = Tk()
    root.withdraw()
    selectedDir = filedialog.askdirectory(initialdir=os.getcwd())
    return selectedDir

def catalogueCurrentFiles(cwd):
    arr = os.listdir(cwd)
    for file in arr:
        if file == ".swm":
            continue
        filePath = os.path.join(cwd, file);
        fileIds[filePath] = int(os.path.getctime(filePath) * FILEID_FACTOR)
        updateFile(cwd, fileIds[filePath], filePath)

def getCredentials(cwd):
    f = open(os.path.join(cwd, ".swm"), "r")
    username = f.readline().strip()
    password = f.readline().strip()
    return username, password

def updateFile(cwd, fileId, filePath):
    username, password = getCredentials(cwd)
    dataObj = {
        "username": username,
        "password": password,
        "fileId": fileId
    }
    print("Sending file", filePath, fileId)
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
        fId = 0
        filePath = ""

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
            if action == 1: # Created
                fileIds[filePath] = int(os.path.getctime(filePath) * FILEID_FACTOR)
                fId = fileIds[filePath]
            elif action == 2: # Deleted
                fId = fileIds[filePath]
                fileIds.pop(filePath)
            elif action == 3: # Modified
                fId = fileIds[filePath]
            elif action == 4: # Renamed from
                fId = fileIds[filePath]
                fileIds.pop(filePath)
            elif action == 5: # Renamed to
                fileIds[filePath] = int(os.path.getctime(filePath) * FILEID_FACTOR)
                fId = fileIds[filePath]
            print(ACTIONS.get(action, "Unknown"), filePath, fId)

        if fId and os.path.isfile(filePath):
            updateFile(cwd, fId, filePath)

def main():
    dir = getWorkingDir()
    catalogueCurrentFiles(dir)
    workloop(dir)

if __name__ == "__main__":
    main()
