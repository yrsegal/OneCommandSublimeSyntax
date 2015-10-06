import sublime, sublime_plugin
import os, sys
import OneCommand

filepath = os.getcwd()

class Minecraft1ccBase(sublime_plugin.TextCommand):

	mode = ""

	def run(self, edit):
		fname = self.view.file_name()
		document = self.view.substr(sublime.Region(0, self.view.size()))

		if fname:
			context = os.path.dirname(fname)
		elif self.view.window().folders():
			context = self.view.window().folders()
		else:
			context = None


		init_commands, clock_commands = OneCommand.parse_commands(document.split("\n"), context)
		final_command = OneCommand.gen_stack(init_commands, clock_commands, self.mode)

		if len(final_command) > 32500:
			sublime.error_message("Resultant command too large ({} > 32500)".format(len(final_command)))
		else:
			views = self.view.window().views()
			check = filter(lambda x: x.name() == "Generated Command", views)
			if len(check):
				view = list(check)[0]
				view.erase(edit, sublime.Region(0, view.size()))
				self.view.window().focus_view(view)
			else:
				view = self.view.window().new_file()
				view.set_scratch(True)
				view.set_name("Generated Command")
				view.set_syntax_file(os.path.join(filepath, "1cc.tmLanguage"))
			view.insert(edit, 0, final_command)
			view.sel().add(sublime.Region(0, view.size()))



class MinecraftOneccManualCommand(Minecraft1ccBase):
	mode = "m"

class MinecraftOneccInstantCommand(Minecraft1ccBase):
	mode = "i"