import importlib.util
import inspect
import sys
from importlib.machinery import ModuleSpec
from pathlib import Path

import pyrogram
from pyrogram.types import MessageEntity
# ----------- #


def module_from_file_location(file_location: str): # type: ignore
	file_location: Path = Path(file_location)
	spec: ModuleSpec = importlib.util.spec_from_file_location(file_location.stem, str(file_location)) # type: ignore
	mod = importlib.util.module_from_spec(spec)
	sys.modules[file_location.name] = mod
	spec.loader.exec_module(mod) # type: ignore
	return mod

def add_entities_text(entities: list[MessageEntity], text: str) -> list[MessageEntity]:
	for entity in entities:
		start = entity.offset
		end = start + entity.length

		entity.text = text[start:end] # type: ignore

	return entities

types = module_from_file_location("C:/Users/User/OneDrive/desktop/python/Pydroid3/bot_playground/neogram/types/pyro.py")
Message = types.Message

def main():
	pyro = Path(inspect.getfile(pyrogram))
	utils = pyro / "utils.py"
	with open(utils, "+w") as f:
		rl = f.readlines()
		if rl[0] != "import pyrogram_extensions as extensions":
			rl.insert(0, "import pyrogram_extensions as extensions")
			f.writelines(rl)
		print("Insert `entities = extensions.add_entities_text(entities, text)` after else block (line 355) in file:\n", utils)

	dispatcher = pyro / "dispatcher.py"
	with open(dispatcher, "+w") as f:
		rl = f.readlines()
		if rl[0] != "import pyrogram_extensions as extensions":
			rl.insert(0, "import pyrogram_extensions as extensions")
			f.writelines(rl)
		print("Insert `pyrogram.types.Message = extensions.Message` after message_parser definition (line 72) in file:\n", dispatcher)