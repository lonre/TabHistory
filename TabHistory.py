# coding: utf-8

"""
Copyright (c) 2013 Lonre Wang

Licensed under The MIT License
"""

import sublime
import sublime_plugin
import os


class TabHistoryCommand(sublime_plugin.WindowCommand):

    last_item = None
    all_tabs = []
    closed_tabs = []

    def run(self, cmd='', args=[]):
        if cmd == 'close':
            self.file_closed(args[0])
            return

        self.all_tabs = self.cal_all_tabs()
        self.window.show_quick_panel(self.tab_names(), self.on_done)

    def on_done(self, selected):
        if selected == -1:
            return
        self.last_item = self.window.active_view()
        selected_item = self.all_tabs[selected]
        if isinstance(selected_item, sublime.View):
            self.window.focus_view(selected_item)
        else:
            self.window.open_file(selected_item)

    def cal_all_tabs(self):
        tabs = []
        views = self.window.views()
        for v in views:
            if v.file_name() in self.closed_tabs:
                self.closed_tabs.remove(v.file_name())
        tabs.extend(views)
        tabs.extend(self.closed_tabs)
        if self.last_item in tabs:
            tabs.remove(self.last_item)
            tabs.insert(0, self.last_item)
        return tabs

    def tab_names(self):
        tab_names = []
        for v in self.all_tabs:
            file_name = v
            if isinstance(v, sublime.View):
                file_name = v.file_name()
                if v.is_dirty():
                    file_name = '* ' + file_name
            if file_name is not None:
                tab_names.append(file_name)
            else:
                tab_names.append('untitled')
        folders = self.window.project_data().get('folders')
        if folders and isinstance(folders, list):
            file_paths = [folder.get('path') for folder in folders]
            for index, name in enumerate(tab_names):
                for p in file_paths:
                    if name.startswith(p):
                        tab_names[index] = os.path.relpath(name, p)
                        break

        return tab_names

    def file_closed(self, file_name):
        self.last_item = file_name
        if file_name in self.closed_tabs:
            return  # return without caring about sorting
        self.closed_tabs.insert(0, file_name)
        if len(self.closed_tabs) > 30:
            self.closed_tabs.pop()


class TabHistoryEvent(sublime_plugin.EventListener):
    def on_close(self, view):
        if view.file_name() and sublime.active_window():
            sublime.active_window().run_command('tab_history', {'cmd': 'close', 'args': [view.file_name()]})
