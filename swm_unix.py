import os
import platform
import time
import requests

from swm_client import Client
from swm_client import FILEID_FACTOR
from swm_client import fileIds
from swm_client import updateFile

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

username = ""
password = ""

def creation_date(path_to_file):
    stat = os.stat(path_to_file)
    try:
        return int(stat.st_birthtime * FILEID_FACTOR)
    except AttributeError:
        # We're probably on Linux. No easy way to get creation dates here,
        # so we'll settle for when its content was last modified.
        return int(stat.st_mtime * FILEID_FACTOR)


def catalogueCurrentFiles(cwd):
    global fileIds
    arr = os.listdir(cwd)
    for file in arr:
        if file == ".swm":
            continue
        filePath = os.path.join(cwd, file)
        fileIds[filePath] = creation_date(filePath)

class Watcher:
    def __init__(self, dir, _username, _password):
        global username
        global password
        self.observer = Observer()
        self.directory = dir
        username = _username
        password = _password

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

        global fileIds
        fId = 0
        if event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)
            filePath = os.path.abspath(event.src_path)
            fileIds[tilePath] = creation_date(filePath)
            fId = fileIds[filePath]

        elif event.event_type == 'deleted':
            # Taken any action here when a file is modified.
            print("Received deleted event - %s." % event.src_path)
            filePath = os.path.abspath(event.src_path)
            fileIds.pop(filePath)

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)
            filePath = os.path.abspath(event.src_path)
            fId = fileIds[filePath]

        elif event.event_type == 'moved':
            # Taken any action here when a file is moved.
            print("Received moved event - %s." % event.src_path)
            filePath = os.path.abspath(event.src_path)
            fId = fileIds[filePath]
            fileIds.pop(filePath)
            if fId and not os.path.isdir(filePath):
                updateFile(username, password, 'renamed_from', fId, filePath)

            new_file = os.path.abspath(event.dest_path)
            fileIds[new_file] = fId
            if fId and not os.path.isdir(filePath):
                updateFile(username, password, 'renamed_to', fId, new_file)
            return

        if fId and not os.path.isdir(filePath):
            updateFile(username, password, event.event_type, fId, filePath)
