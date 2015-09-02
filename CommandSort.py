import sublime, sublime_plugin, re

selector_regex = re.compile(r"@[prae]\[[\w!_=,]*\]")

class MinecraftSortSelectorCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():

			# If no selection, use the entire file as the selection
			if region.empty():
				selection = sublime.Region(0, self.view.size())
			else:
				selection = region

			text = self.view.substr(selection)
			matches = selector_regex.findall(text)
			for selector in matches:
				selector_base = selector[1]
				selector_tags = selector[3:-1].split(",")
				selector_tags.sort()
				newselector = "@{0}[{1}]".format(selector_base, ",".join(selector_tags))
				text = text.replace(selector, newselector)
			self.view.replace(edit, selection, text)