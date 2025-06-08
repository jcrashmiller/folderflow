#!/usr/bin/env python3
import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('smart_folders')

class SmartFolderHandler(FileSystemEventHandler):
    def __init__(self, config_path, update_callback):
        self.config_path = config_path
        self.update_callback = update_callback
        self.last_update = 0
        self.update_delay = 2
        logger.debug(f"Handler initialized for {config_path}")

    def on_any_event(self, event):
        logger.info(f"Event type: {event.event_type}")
        logger.info(f"Event path: {event.src_path}")

        # Only trigger on actual file changes
        if event.event_type in ('created', 'modified'):
            current_time = time.time()
            if current_time - self.last_update > self.update_delay:
                self.last_update = current_time
                self.update_callback(self.config_path)

def update_folder(config_path):
    folder_name = os.path.splitext(os.path.basename(config_path))[0]
    script_path = "/usr/local/bin/smart-folders.sh"
    logger.info(f"Updating folder: {folder_name}")
    try:
        result = subprocess.run([script_path, "update", folder_name],
                              capture_output=True, text=True)
        logger.debug(f"Update result: {result.stdout}")
        if result.stderr:
            logger.error(f"Update error: {result.stderr}")
    except Exception as e:
        logger.error(f"Update exception: {str(e)}")

def monitor_folders():
    config_dir = os.path.expanduser("~/.smart_folders/configs")
    observers = []

    while True:
        try:
            logger.info(f"Scanning config directory: {config_dir}")
            for config in os.listdir(config_dir):
                if config.endswith('.conf'):
                    config_path = os.path.join(config_dir, config)
                    with open(config_path) as f:
                        config_content = f.read()
                        logger.info(f"Full config for {config}: {config_content}")
                        for line in config_content.splitlines():
                            if line.startswith('SEARCH_DIR='):
                                search_dir = line.split('"')[1]
                                break

                    logger.debug(f"Setting up observer for {search_dir}")
                    observer = Observer()
                    handler = SmartFolderHandler(config_path, update_folder)
                    observer.schedule(handler, search_dir, recursive=True)
                    observer.start()
                    observers.append(observer)

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            for observer in observers:
                observer.stop()
            for observer in observers:
                observer.join()
            break
        except Exception as e:
            logger.error(f"Monitor exception: {str(e)}")

if __name__ == "__main__":
    monitor_folders()
