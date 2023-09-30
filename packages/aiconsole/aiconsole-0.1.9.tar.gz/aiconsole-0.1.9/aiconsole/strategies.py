import importlib.util
import os
from typing import Dict
import watchdog.observers
import watchdog.events
from importlib.resources import path as resource_path
from aiconsole.aic_types import Strategy
from aiconsole.copy_presets_to_cwd import copy_presets_to_cwd
from aiconsole.execution_modes.interpreter import execution_mode_interpreter
from aiconsole.execution_modes.normal import execution_mode_normal

STRATEGIES_DIRECTORY = "./strategies"
PRESET_STRATEGIES_DIRECTORY = resource_path("aiconsole.presets", "strategies")


class Strategies:
    """
    Manuals class is for managing the .md and .py manual files.
    """

    strategies: Dict[str, Strategy]

    def __init__(self):
        self.strategies = {}

        copy_presets_to_cwd("strategies")

        observer = watchdog.observers.Observer()

        parent = self

        class Handler(watchdog.events.FileSystemEventHandler):
            def on_modified(self, event):
                if event.is_directory or not event.src_path.endswith(".py"):
                    return
                parent.reload()

        observer.schedule(Handler(), STRATEGIES_DIRECTORY, recursive=True)

        observer.start()
        self.reload()

    def all_strategies(self):
        """
        Return all loaded materials.
        """
        return list(self.strategies.values())

    def reload(self):
        print("Reloading strategies ...")

        execution_modes = {
            "interpreter": execution_mode_interpreter,
            "normal": execution_mode_normal,
        }

        self.strategies = {}
        for filename in os.listdir(STRATEGIES_DIRECTORY):
            if filename.endswith(".py"):
                # Check if the first line of the file is '# Strategy'
                with open(os.path.join(STRATEGIES_DIRECTORY, filename), "r") as file:
                    first_line = file.readline().strip()
                    if first_line != "# Strategy":
                        print(f"Skipping invalid strategy in file {filename}")
                        continue

                # Import the file and execute manual function to get the manual
                path = os.path.join(STRATEGIES_DIRECTORY, filename)
                module_name = os.path.splitext(filename)[0]
                spec = importlib.util.spec_from_file_location(module_name, path)
                if not spec or spec.loader is None:
                    print(f"Skipping invalid strategy in file {filename}")
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                strategy = module.strategy
                self.strategies[strategy["id"]] = Strategy(
                    id=strategy["id"],
                    usage=strategy["usage"],
                    system=strategy["system"],
                    execution_mode=execution_modes[strategy["execution_mode"]],
                )

        print(f"Reloaded {len(self.strategies)} strategies")


strategies = Strategies()
