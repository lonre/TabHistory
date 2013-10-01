# coding: utf-8

"""
Copyright (c) 2013 Lonre Wang

Licensed under The MIT License
"""

import sublime
import sublime_plugin
import os


class TabHistoryCommand(sublime_plugin.WindowCommand):

    last_item, all_tabs, closed_tabs = None, [], []

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
        tabs, views = [], self.window.views()
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
        tab_names, folder_paths = [], []
        folders = self.window.project_data().get('folders')
        if folders and isinstance(folders, list):
            folder_paths = [folder.get('path') for folder in folders]
        for v in self.all_tabs:
            is_view = is_dirty_view = False
            file_name = v
            if isinstance(v, sublime.View):
                file_name = v.file_name()
                is_view, is_dirty_view = True, v.is_dirty()
            if file_name is not None:
                for p in folder_paths:
                    if file_name.startswith(p):
                        file_name = os.path.relpath(file_name, p)
                        if is_view and is_dirty_view:
                            file_name = '* ' + file_name
                        if not is_view:
                            file_name = 'x ' + file_name
                        break
                tab_names.append(file_name)
            else:
                tab_names.append('untitled')

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
