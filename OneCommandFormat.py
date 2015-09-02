"""
Minecraft Command Formatter for Sublime Text

One Command edition - @wiresegal

Simply select the command you want to format and run this plugin

Feel free to use and edit, just give credit to TheDestruc7i0n and @Texelelf.
http://thedestruc7i0n.ca
https://twitter.com/TexelElf
"""

import sublime, sublime_plugin, re
dash_regex =  re.compile(r"^[ \t]*-")
end_regex =   re.compile(r"\n$")
tab_regex =   re.compile(r"- \t+")

ready_regex = re.compile(r"\[|\{")

class MinecraftFormatBaseCommand(sublime_plugin.TextCommand):

	""" Base code | Majority is from @TexelElf """

	@staticmethod
	def indent(ct, space=False):
		sp = " " if space else ""
		return "\t"*(ct+1) +"-{0}\t".format(sp)

	@staticmethod
	def dashsub(string):
		if dash_regex.match(string):
			return dash_regex.sub("", tab_regex.sub("- ", string)).lstrip("\t").rstrip(" ")
		return string.rstrip(" ")

	def strexplode(self, command):
		coms = []
		if not command:
			return coms
		i = 0
		line = ""
		inquote = 0
		for c in xrange(len(command)):
			if command[c] == "{":
				if inquote:
					line += command[c]
				else:
					if line:
						coms.append(self.indent(i)+line+"\n")
						line = ""
					space = command[c-1] == " "
					coms.append(self.indent(i, space)+"{\n")
					i += 1
			elif command[c] == "}":
				if inquote:
					line += command[c]
				else:
					if line:
						coms.append(self.indent(i)+line+"\n")
						line = ""
					i -= 1
					line += command[c]
			elif command[c] == "[":
				if inquote:
					line += command[c]
				else:
					if line:
						coms.append(self.indent(i)+line+"\n")
						line = ""
					space = command[c-1] == " "
					coms.append(self.indent(i, space)+"[\n")
					i += 1
			elif command[c] == "]":
				if inquote:
					line += command[c]
				else:
					if line:
						coms.append(self.indent(i)+line+"\n")
						line = ""
					i -= 1
					line += command[c]
			elif command[c] == '\"':
				toappend = "\""
				if command[c-1] == " " and not inquote:
					toappend = " " + toappend
				if command[c-1] != "\\":
					inquote ^= 1
				line += toappend
			elif command[c] == ",":
				if inquote:
					line += command[c]
				else:
					coms.append(self.indent(i)+line+",\n")
					line = ""
			elif command[c] == " ":
				if c:
					line += " "
			else:
				line += command[c]
		else:
			if line:
				coms.append(self.indent(i)+line+"\n")
		return coms


	def strcollapse(self, lines):
		command = ""
		for l in lines:
			if not l:
				continue
			elif l is not lines[-1] and dash_regex.match(lines[lines.index(l)+1]):
				command += self.dashsub(l.rstrip("\n"))
			else:
				command += self.dashsub(l)
		return command
				
class MinecraftOneccFormatCommand(MinecraftFormatBaseCommand):
	
	""" Pretty Print a Minecraft Command """

	def run(self, edit):
		outputlines = []
		for region in self.view.sel():

			# If no selection, use the entire file as the selection
			if region.empty():
				selection = sublime.Region(0, self.view.size())
			else:
				selection = region

			if not selection.contains(0):
				if self.view.substr(sublime.Region(selection.begin()-1, selection.begin())) == " ":
					selection = sublime.Region(selection.begin()-1, selection.end())

			fs = self.view.substr(selection)

			if ready_regex.search(fs):
				mdatapos = ready_regex.search(fs).start()
				if mdatapos: mdatapos -= 1
				outputlines.append(fs[:mdatapos]+"\n")
				outputlines+=self.strexplode(fs[mdatapos:])
			else:
				outputlines.append(str(fs)+"\n")
			out = end_regex.sub("", "".join(outputlines))

			self.view.replace(edit, selection, out)

class MinecraftOneccUnformatCommand(MinecraftFormatBaseCommand):

	""" Bring Pretty Printed Command Back To String """

	def run(self, edit):
		for region in self.view.sel():

			# If no selection, use the entire file as the selection
			if region.empty():
				selection = sublime.Region(0, self.view.size())
			else:
				selection = region

			fs = self.view.substr(selection).splitlines(True)

			output = self.strcollapse(fs)

			self.view.replace(edit, selection, output)
