
import os
import win32file
import win32con
from tkinter import filedialog
from tkinter import *

ACTIONS = {
    1 : "Created",
    2 : "Deleted",
    3 : "Modified",
    4 : "Renamed from",
    5 : "to"
}
FILE_LIST_DIRECTORY = 0x0001

def getDir():
    root = Tk()
    root.withdraw()
    selectedDir = filedialog.askdirectory(initialdir=os.getcwd())
    return selectedDir

def workloop(dir):
    print("Running SWM client in " + dir)
    dirHandle = win32file.CreateFile(
                dir, 
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
            fullPath = os.path.join(dir, file)
            print(ACTIONS.get(action, "Unknown"), fullPath)


def main():
    dir = getDir()
    workloop(dir)



if __name__ == "__main__":
    main()
