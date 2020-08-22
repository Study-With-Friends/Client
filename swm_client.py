import os
from tkinter import filedialog
from tkinter import *
import requests
import platform
import time

FILEID_FACTOR = 1000000

URL = "http://localhost:5000/v1/files/upload"
fileIds = {}

def updateFile(username, password, action, fileId, filePath):
    if os.path.isdir(filePath):
        return
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

class Client:
    def __init__(self):
        self.cwd = self.getWorkingDir()
        self.username, self.password = self.getCredentials(self.cwd)        
        
    def getWorkingDir(self):
        root = Tk()
        root.withdraw()
        selectedDir = filedialog.askdirectory(initialdir=os.getcwd())
        return selectedDir

    def getCredentials(self, cwd):
        try:
            f = open(os.path.join(cwd, ".swm"), "r")
            newUsername = f.readline().strip()
            newPassword = f.readline().strip()
            return (newUsername, newPassword)
        except Exception as e:
            print(e)
            return None, None            

def main():
    client = Client()

    print("Running SWM client in " + client.cwd)
    if platform.system() == 'Windows':
        import swm_windows
        swm_windows.catalogueCurrentFiles(client)
        swm_windows.workloop(client)
    else:
        import swm_unix
        swm_unix.catalogueCurrentFiles(client.cwd)
        w = swm_unix.Watcher(str(client.cwd), str(client.username), str(client.password))
        w.run()

if __name__ == "__main__":
    main()
