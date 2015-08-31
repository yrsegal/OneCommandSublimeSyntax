import sublime, sublime_plugin
import os, sys
sys.path.append(os.path.join(os.getcwd(), "OneCommand"))
import oneCommand

class Minecraft1ccBase(sublime_plugin.TextCommand):

	mode = ""

	def run(self, edit):
		fname = self.view.file_name()
		document = self.view.substr(sublime.Region(0, self.view.size()))

		init_commands, clock_commands = oneCommand.parse_commands(document.split("\n"))
		final_command = oneCommand.gen_stack(init_commands, clock_commands, self.mode)

		if len(final_command) > 32500:
			sublime.error_message("Resultant command too large ({} > 32500)".format(len(final_command)))
		else:
			new_view = self.view.window().new_file()
			new_view.set_syntax_file("Packages/OneCommandSublimeSyntax/1cc.tmLanguage")
			new_view.insert(edit, 0, final_command)
			new_view.sel().add(sublime.Region(0, new_view.size()))



class MinecraftOneccManualCommand(Minecraft1ccBase):
	mode = "m"

class MinecraftOneccInstantCommand(Minecraft1ccBase):
	mode = "i"