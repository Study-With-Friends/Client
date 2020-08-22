import os
from tkinter import filedialog
from tkinter import *
import requests
import platform
import time

# unix imports
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ACTIONS = {
    1 : "Created",
    2 : "Deleted",
    3 : "Modified",
    4 : "Renamed from",
    5 : "Renamed to"
}
FILE_LIST_DIRECTORY = 0x0001

URL = "https://3affc17a5073.ngrok.io/v1/files/upload"
fileIds = {}

email = None
password = None

def getWorkingDir():
    root = Tk()
    root.withdraw()
    selectedDir = filedialog.askdirectory(initialdir=os.getcwd())
    return selectedDir

def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime

def catalogueCurrentFiles(cwd):
    arr = os.listdir(cwd)
    for file in arr:
        fileIds[file] = creation_date(os.path.join(cwd, file))

def getCredentials(cwd):
    try:
        f = open(os.path.join(cwd, ".swm"), "r")
        new_email = f.readline().strip()
        new_password = f.readline().strip()
        return new_email, new_password
    except:
        return None, None

def updateFile(action, fileId, filePath):
    dataObj = {
        "action": action,
        "email": email,
        "password": password,
        "fileId": fileId
    }
    print(f"Sending file: {action}, {email}, {password}, {fileId}")

def workloop(cwd):
    # windows imports
    import win32file
    import win32con
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
                fileIds[file] = creation_date(filePath)
                fId = fileIds[file]
            elif action == 2: # Deleted
                fId = fileIds[file]
                fileIds.pop(file)
            elif action == 3: # Modified
                fId = fileIds[file]
            elif action == 4: # Renamed from
                fId = fileIds[file]
                fileIds.pop(file)
            elif action == 5: # Renamed to
                fileIds[file] = creation_date(filePath)
                fId = fileIds[file]
            print(ACTIONS.get(action, "Unknown"), filePath, fId)

        if fId and os.path.isfile(filePath):
            updateFile(cwd, fId, filePath)

class Watcher:
    def __init__(self, dir):
        self.observer = Observer()
        self.directory = dir

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.directory, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        fId = 0
        filePath = event.src_path
        if event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)
            file = os.path.basename(event.src_path)
            fileIds[file] = creation_date(filePath)
            fId = fileIds[file]
            # TODO: send event to create

        elif event.event_type == 'deleted':
            # Taken any action here when a file is modified.
            print("Received deleted event - %s." % event.src_path)
            file = os.path.basename(event.src_path)
            fileIds.pop(file)

            # TODO: send event to delete

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)
            file = os.path.basename(event.src_path)
            fId = fileIds[file]

            # TODO: send event to update

        elif event.event_type == 'moved':
            # Taken any action here when a file is moved.
            print("Received moved event - %s." % event.src_path)
            file = os.path.basename(event.dest_path)
            fId = fileIds[file]
            fileIds.pop(file)

            # TODO: send event to remove
            new_file = os.path.basename(event.dest_path)
            fId = fileIds[file]
            # TODO: send event to add


        if fId and os.path.isfile(filePath):
            updateFile(event.event_type, fId, filePath)

def main():
    dir = getWorkingDir()
    if not dir:
        return

    catalogueCurrentFiles(dir)
    email, password = getCredentials(dir)

    if not email or not password:
        print("No .swm file found in directory. Please create one with your username and password.")
        return

    print("Running SWM client in " + dir)
    if platform.system() == 'Windows':
        workloop(dir)
    else:
        w = Watcher(dir)
        w.run()

if __name__ == "__main__":
    main()
