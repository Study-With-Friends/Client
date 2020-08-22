import os
import platform
import time
import requests

from swm_client import FILEID_FACTOR
from swm_client import fileIds
from swm_client import updateFile

def creation_date(path_to_file):
    stat = os.stat(path_to_file)
    try:
        return int(stat.st_birthtime * FILEID_FACTOR)
    except AttributeError:
        # We're probably on Linux. No easy way to get creation dates here,
        # so we'll settle for when its content was last modified.
        return int(stat.st_mtime * FILEID_FACTOR)


def catalogueCurrentFiles(cwd):
    arr = os.listdir(cwd)
    for file in arr:
        if file == ".swm":
            continue
        filePath = os.path.join(cwd, file)
        fileIds[filePath] = creation_date(filePath)

class Watcher:
    def __init__(self, dir):
        self.observer = Observer()
        self.directory = dir

    def run(self):
        # unix imports
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            pass
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
