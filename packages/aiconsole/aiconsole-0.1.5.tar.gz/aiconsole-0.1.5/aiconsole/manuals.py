import importlib.util
import os
import shutil
from typing import Dict
import watchdog.observers
import watchdog.events
import re

from aiconsole.aic_types import Manual

MANUALS_DIRECTORY = "./manuals"
PRESET_MANUALS_DIRECTORY = "./presets/manuals"

class ManualsHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self, manuals):
        super().__init__()
        self.manuals = manuals

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return
        self.manuals.reload()

class Manuals:
    """
    Manuals class is for managing the .md and .py manual files.
    """

    manuals: Dict[str, Manual]

    def __init__(self):
        self.manuals = {}
        

        if not os.path.exists(MANUALS_DIRECTORY):
            print("Creating manuals directory from presets")
            os.mkdir(MANUALS_DIRECTORY)
            for filename in os.listdir(PRESET_MANUALS_DIRECTORY):
                if filename.endswith('.md') or filename.endswith('.py'):
                    shutil.copy(os.path.join(PRESET_MANUALS_DIRECTORY, filename),
                        os.path.join(MANUALS_DIRECTORY, filename))
        
        observer = watchdog.observers.Observer()
        observer.schedule(ManualsHandler(self), MANUALS_DIRECTORY, recursive=True)
        observer.start()
        self.reload()

    def all_manuals(self):
        """
        Return all loaded materials.
        """
        return list(self.manuals.values())

    def delete_manual(self, name):
        """
        Delete a specific material.
        """
        if name not in self.manuals:
            raise KeyError(f'Material {name} not found')
        del self.manuals[name]

    def reload(self):
        print('Reloading manuals ...')

        self.manuals = {}
        for filename in os.listdir(MANUALS_DIRECTORY):
            if filename.endswith('.py'):
                # Check if the first line of the file is '# Manual'
                with open(os.path.join(MANUALS_DIRECTORY, filename), 'r') as file:
                    first_line = file.readline().strip()
                    if first_line != '# Manual':
                        print(f'Skipping invalid manual in file {filename}')
                        continue

                # Import the file and execute manual function to get the manual
                path = os.path.join(MANUALS_DIRECTORY, filename)
                module_name = os.path.splitext(filename)[0]
                spec = importlib.util.spec_from_file_location(module_name, path)
                if not spec or spec.loader is None:
                    print(f'Skipping invalid manual in file {filename}')
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                manual = module.manual
                self.manuals[manual["id"]] = Manual(
                    id=manual["id"],
                    usage=manual["usage"],
                    content=manual["content"]
                )
            elif filename.endswith('.md'):
                path = os.path.join(MANUALS_DIRECTORY, filename)
                with open(path, 'r') as file:
                    lines = file.readlines()

                    # Merging all lines into a single string
                    text = ''.join(lines)

                    pattern = r"\s*(<!---|<!--)\s*(.*?)\s*(-->)\s*(.*)\s*"

                    match = re.match(pattern, text.strip(), re.DOTALL)

                    if not match:
                        print(f'Skipping invalid manual in file {filename}')
                        continue
                    
                    # Extracting 'usage' and 'content' based on matched groups
                    usage = match.group(2)
                    content = match.group(4)

                    # Pruning leading/trailing spaces and newlines (if any)
                    usage = usage.strip()
                    content = content.strip()

                    manual_id = os.path.splitext(filename)[0]
                    self.manuals[manual_id] = Manual(
                        id=manual_id,
                        usage=usage,
                        content=lambda context: content
                    )

        print(f'Reloaded {len(self.manuals)} manuals')