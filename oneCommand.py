from __future__ import print_function

from util import *
import nbtencoder as nbt

import re
import argparse
import sys, os

cprintconf.name = "Generator"
cprintconf.color = bcolors.PEACH

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode", help="Choose activation mode for system", dest="mode", default="", choices=["m", "i"])
parser.add_argument("-f", "--command_file", help="File to load commands from", dest="filepath",
	default=None)
parser.add_argument("-C", "--no-copy", help="Don't copy the output command", dest="nocopy", action="store_true")
parser.add_argument("-q", "--quiet", help="Silence output", dest="quiet", action="store_true")
parser.add_argument("-v", "--verbose", help="Detailed output", dest="loud", action="store_true")
parser.add_argument("-O", "--no-output", help="Don't dump cmd to STDOUT", dest="nostdout", action="store_true")

class Command:
	def __init__(self, cmd, init=False, conditional=False, variables=[]):
		self.cmd = cmd
		self.cond = conditional
		self.init = init
		for i in variables:
			self.cmd = i.sub(self.cmd)
	def __str__(self):
		return self.cmd
	def prettystr(self):
		return format("{cmd}{init}{cond}",
			cmd = self.cmd,
			init = "\n  - Initialization" if self.init else "",
			cond = "\n  - Conditional" if self.cond else "")

class CmdVariable:
	def __init__(self, name, replacewith):
		self.name = name
		self.replacewith = replacewith
		self.regex = re.compile("\\$"+name.lower()+"\\b", re.IGNORECASE)
	def sub(self, string):
		return self.regex.sub(self.replacewith, string)


def generate_sand(command_obj, direction, block="chain_command_block"):
	tag = {
		"Block": block,
		"Time": 1,
		"TileEntityData": {
			"Command": str(command_obj),
			"TrackOutput": nbt.int_b(0)
		},
		"id": "FallingSand"
	}
	data = direction+8 if command_obj.cond else direction
	if data:
		tag["Data"] = data
	return tag


def normal_sand(block, data=0):
	tag = {
		"Block": block,
		"Time": 1,
		"id": "FallingSand"
	}
	if data:
		tag["Data"] = data
	return tag

def gen_stack(init_commands, clock_commands, mode, loud=False):
	final_command_obj = None
	if clock_commands or init_commands:
		command_sands = []

		for command in init_commands:
			if loud:
				cprint(command.prettystr())
			if command is init_commands[0]:
				topsand = generate_sand(command, 0, "command_block")
				topsand["TileEntityData"]["auto"] = 1
				command_sands.append(topsand)
			else:
				command_sands.append(generate_sand(command, 0))

		if mode == 'i' and clock_commands:
			block = "command_block" if not init_commands else "chain_command_block"
			offset = len(clock_commands) + 2
			blockdata = Command(format("blockdata ~ ~-{offset} ~ {auto:1b}", offset = offset), init=True)
			if loud:
				cprint(blockdata.prettystr())
			sand = generate_sand(blockdata, 0, block)
			if not init_commands:
				sand["TileEntityData"]["auto"] = 1
			command_sands.append(sand)

		offset = len(init_commands) + int(bool(mode == 'i' and clock_commands))
		if offset:
			fill = Command(format("fill ~ ~-1 ~ ~ ~{offset} ~ air", offset = offset), init=True)
			if loud:
				cprint(fill.prettystr())
			command_sands.append(generate_sand(fill, 0))
			command_sands.append(normal_sand("barrier"))

		for command in clock_commands[::-1]:
			if loud:
				cprint(command.prettystr())
			if command is clock_commands[0]:
				command_sands.append(generate_sand(command, 1, "repeating_command_block"))
			else:
				command_sands.append(generate_sand(command, 1))
		final_command_obj = nbt.cmd("summon FallingSand ~ ~1 ~ ", ride(command_sands, False))

	final_command = nbt.JSON2Command(final_command_obj)

	return final_command

def parse_commands(commands):
	init_commands = []
	clock_commands = []
	variables = []
	varnames = []
	# do all INIT and COND checking
	for command in commands:
		command = command.strip().rstrip()
		if not command: continue
		if command[0] == "#": 
			continue

		if command.lower()[:7] == "define:":
				command_split = command[7:].split()
				while not command_split[0]:
					command_split = command_split[1:]
				while not command_split[1]:
					command_split = command_split[:1] + command_split[2:]
				if len(command_split) < 2: continue
				name = command_split[0]
				contents = " ".join(command_split[1:])
				for i in variables:
					name = i.sub(name)
					contents = i.sub(contents)

				if name in varnames: 
					cprint("WARNING: Duplicate variable {var}. Using first definition.", color=bcolors.YELLOW, var=name)
				else:
					varnames.append(name)
					variables.append(CmdVariable(name, contents))

		init = False
		conditional = False
		while command[:5].lower() in ["init:","cond:"]:
			if command[:5].lower() == "cond:": conditional = True
			elif command[:5].lower() == "init:": init = True
			command = command[5:]
		command = command.strip().rstrip()
		command_obj = Command(command, conditional=conditional, init=init, variables=variables)
		if init:
			init_commands.append(command_obj)
		else:
			clock_commands.append(command_obj)
	return init_commands, clock_commands

def ride(entities, have_id=True):
	topmost = None
	absoluteTopmost = None
	
	for entity in entities:
		if topmost == None:
			absoluteTopmost = entity
		else:
			topmost["Riding"] = entity
		topmost = entity
	if not have_id: del absoluteTopmost["id"]
	return absoluteTopmost

if __name__ == "__main__":
	args = parser.parse_args()
	if args.quiet:
		def cprint(*args, **kwargs):
			pass

	if args.nocopy:
		class pyperclip:
			@staticmethod
			def copy(*args, **kwargs): pass
			@staticmethod
			def paste(*args, **kwargs): pass
	else:
		import pyperclip

	cprint("""{peach}----------------------------------------{endc}
	  {cyan}TheDestruc7i0n{endc} and {golden}Wire Segal{endc}'s 1.9 One Command Generator
	 {green}Prepend your command with `#` to comment it out.{endc}
	 {green}Prepend your command with `DEFINE:` to make it a variable definition.{endc}
	        Example: `DEFINE:world hello` and `say $world` would say `hello`.
	 {green}Prepend your command with `INIT:` to make it only run when the structure is deployed.{endc}
	 {green}Prepend your command with `COND:` to make it a conditional command.{endc}
	        Please report any bugs at the GitHub repo: {line}{blue}https://github.com/destruc7i0n/OneCommand/issues{endc}
	        {peach}----------------------------------------{endc}""", strip=True)

	# get mode if not specified by argument
	if not args.mode:
		mode = cinput("Manual (m) or Instant (i)? ").strip().rstrip().lower()
		if mode not in ["m", "i"]:
			raise ValueError("Not manual or instant")
	else:
		mode = args.mode

	commands = []
	# get commands if file not specified
	if not args.filepath:
		x = 1
		command = cinput("Command {num}: ", num=x).strip().rstrip()
		while command:
			x += 1
			commands.append(command)
			command = cinput("Command {num}: ", num=x).strip().rstrip()
	# get commands from specified file
	else:
		if os.path.exists(args.filepath):
			commands = open(args.filepath).read().split("\n")
		else:
			raise IOError(format("File {file} not found.", file=args.filepath))


	init_commands, clock_commands = parse_commands(commands)


	final_command = gen_stack(init_commands, clock_commands, mode, args.loud)
	


	if len(final_command) <= 32500 and final_command:
		pyperclip.copy(final_command)
		if args.nocopy:
			cprint("{bold}Final command{endc}", func=sys.stderr.write)
		else:
			cprint("{bold}Copied to clipboard{endc}", func=sys.stderr.write)
		if not args.nostdout:
			sys.stdout.write(final_command + "\n")
		else:
			sys.stderr.write(format("{bold}.\n{endc}"))
	elif not final_command:
		cprint("No command generated.", color=bcolors.RED)
	else:
		cprint("Command too large ({length} > 32500)", length=len(final_command), color=bcolors.RED)
