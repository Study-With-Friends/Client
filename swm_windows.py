import os
import win32file
import win32con
from tkinter import filedialog
from tkinter import *
import requests

from swm_client import Client
from swm_client import FILEID_FACTOR
from swm_client import fileIds
from swm_client import updateFile

ACTIONS = {
    1: "created",
    2: "deleted",
    3: "modified",
    4: "renamed_from",
    5: "renamed_to"
}
FILE_LIST_DIRECTORY = 0x0001


def getCreateTime(filePath):
    return int(os.path.getctime(filePath) * FILEID_FACTOR)


def catalogueCurrentFiles(client):
    global fileIds
    arr = os.listdir(client.cwd)
    for file in arr:
        if file == ".swm":
            continue
        filePath = os.path.join(client.cwd, file)
        fileIds[filePath] = getCreateTime(filePath)
        updateFile(client.username, client.password, ACTIONS.get(1, "Unknown"), fileIds[filePath], filePath)

def workloop(client):
    global fileIds
    dirHandle = win32file.CreateFile(
        client.cwd,
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
            filePath = os.path.join(client.cwd, file)
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
            
            if fId and not os.path.isdir(filePath):
                updateFile(client.username, client.password, ACTIONS.get(action, "Unknown"), fId, filePath)
