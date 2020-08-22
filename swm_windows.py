import os
import win32file
import win32con
from tkinter import filedialog
from tkinter import *
import requests

from swm_client import FILEID_FACTOR
from swm_client import fileIds
from swm_client import updateFile

ACTIONS = {
    1: "Created",
    2: "Deleted",
    3: "Modified",
    4: "Renamed from",
    5: "Renamed to"
}
FILE_LIST_DIRECTORY = 0x0001


def getCreateTime(filePath):
    return int(os.path.getctime(filePath) * FILEID_FACTOR)


def catalogueCurrentFiles(cwd):
    arr = os.listdir(cwd)
    for file in arr:
        if file == ".swm":
            continue
        filePath = os.path.join(cwd, file)
        fileIds[filePath] = getCreateTime(filePath)

def workloop(cwd):
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
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
            win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
            win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
            win32con.FILE_NOTIFY_CHANGE_SIZE |
            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
            win32con.FILE_NOTIFY_CHANGE_SECURITY,
            None,
            None)
        for action, file in results:
            filePath = os.path.join(cwd, file)
            if action == 1:  # Created
                fileIds[filePath] = getCreateTime(filePath)
                fId = fileIds[filePath]
            elif action == 2:  # Deleted
                fId = fileIds[filePath]
                fileIds.pop(filePath)
            elif action == 3:  # Modified
                fId = fileIds[filePath]
            elif action == 4:  # Renamed from
                fId = fileIds[filePath]
                fileIds.pop(filePath)
            elif action == 5:  # Renamed to
                fileIds[filePath] = getCreateTime(filePath)
                fId = fileIds[filePath]
            print(ACTIONS.get(action, "Unknown"), filePath, fId)

        if fId and os.path.isfile(filePath):
            updateFile(cwd, fId, filePath)
