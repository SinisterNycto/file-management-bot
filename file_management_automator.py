from os import scandir, rename
from os.path import splitext, exists, join
from shutil import move
from time import sleep

import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set your directory paths here
# Example: Windows path: "C:\\Users\\YourName\\Downloads"
watch_folder = ""
audio_sfx_dir = ""
audio_music_dir = ""
video_dir = ""
image_dir = ""
document_dir = ""

# File extensions for categorization
image_formats = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico", ".webp", ".tiff", ".heif", ".psd"]
video_formats = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".webm", ".wmv"]
audio_formats = [".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg"]
document_formats = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"]

def create_unique_name(dest, filename):
    name, ext = splitext(filename)
    counter = 1

    while exists(join(dest, filename)):
        filename = f"{name}({counter}){ext}"
        counter += 1

    return filename

def relocate_file(destination, item, filename):
    if exists(join(destination, filename)):
        filename = create_unique_name(destination, filename)

    move(item.path, join(destination, filename))

def is_file_matching(extension_list, filename):
    return any(filename.lower().endswith(ext) for ext in extension_list)

class FileSorterHandler(FileSystemEventHandler):
    def on_modified(self, event):
        with scandir(watch_folder) as items:
            for item in items:
                if item.is_file():
                    self.handle_file(item)

    def handle_file(self, item):
        filename = item.name

        if is_file_matching(audio_formats, filename):
            destination = audio_sfx_dir if item.stat().st_size < 10_000_000 else audio_music_dir
            relocate_file(destination, item, filename)
            logging.info(f"Audio moved: {filename}")

        elif is_file_matching(video_formats, filename):
            relocate_file(video_dir, item, filename)
            logging.info(f"Video moved: {filename}")

        elif is_file_matching(image_formats, filename):
            relocate_file(image_dir, item, filename)
            logging.info(f"Image moved: {filename}")

        elif is_file_matching(document_formats, filename):
            relocate_file(document_dir, item, filename)
            logging.info(f"Document moved: {filename}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    observer = Observer()
    handler = FileSorterHandler()
    observer.schedule(handler, watch_folder, recursive=True)

    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
