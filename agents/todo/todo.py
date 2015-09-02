#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Zoe Todo - https://github.com/rmed/zoe-todo
#
# Copyright (c) 2015 Rafael Medina García <rafamedgar@gmail.com>
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import gettext
import os
import zoe
from configparser import ConfigParser
from os import environ as env
from os.path import join as path
from zoe.deco import *
from zoe.model.users import Users

gettext.install("todo")

LOCALEDIR = path(env["ZOE_HOME"], "locale")
ZOE_LOCALE = env["ZOE_LOCALE"] or "en"

MSG_CURRENT_NOT_FOUND = _("Did not find current active list")
MSG_LIST_NOT_EXIST = _("List does not exist")
MSG_NO_LISTS = _("There are no lists")

TODO_CURRENT = path(env["ZOE_HOME"], "etc", "current_todo.conf")
TODO_PATH = path(env["ZOE_HOME"], "etc", "todo")


@Agent(name="todo")
class Todo:

    @Message(tags=["add-task"])
    def add_task(self, task, sender, src):
        """ Add a task to current list. """
        self.set_locale(sender)

        current = self.get_current(sender)

        if not current:
            return self.feedback(MSG_CURRENT_NOT_FOUND, sender, src)

        if not self.list_exists(sender, current):
            return self.feedback(MSG_LIST_NOT_EXIST, sender, src)

        tasks = self.read_list(sender, current)

        tasks.append("[ ] " + task)

        self.write_list(tasks, sender, current)

        return self.feedback(_("Added task '%s' to list") % task, sender, src)

    @Message(tags=["change-current"])
    def change_current(self, new_current, sender, src):
        """ Change currently active list for the user.

            If the list does not exist, it will be created.
        """
        self.set_locale(sender)

        self.check_dir(sender)
        list_path = path(TODO_PATH, sender, new_current)

        if not os.path.isfile(list_path):
            with open(list_path, "w"):
                pass

        self.set_current(user, new_current)

        return self.feedback(_("Changed to list '%s'") % new_current,
            sender, src)

    @Message(tags=["create-list"])
    def create_list(self, new_list, sender, src):
        """ Create a new empty list.

            If the list already exist, creation will be cancelled.
        """
        self.set_locale(sender)

        self.check_dir(sender)
        list_path = path(TODO_PATH, sender, new_list)

        if os.path.isfile(list_path):
            return self.feedback(_("List '%s' already exists") % new_list,
                sender, src)

        with open(list_path, "w"):
            pass

        return self.feedback(_("Created new list '%s'") % new_list,
            sender, src)

    @Message(tags=["mark"])
    def mark_task(self, task_num, mark, sender, src):
        """ Mark or unmark a given task in current list.

            The task is searched by index number.
        """
        self.set_locale(sender)

        current = self.get_current(sender)

        if not current:
            return self.feedback(MSG_CURRENT_NOT_FOUND, sender, src)

        if not self.list_exists(sender, current):
            return self.feedback(MSG_LIST_NOT_EXIST, sender, src)

        tasks = self.read_list(sender, current)

        try:
            original = tasks[int(task_num)]
            tasks.remove(original)

            if mark == "0":
                # Unmark
                marked = "[ ] " + original[4:]

            elif mark == "1":
                # Mark
                marked = "[X] " + original[4:]

            else:
                # Not recognized
                return self.feedback(_("Mark not recognized"), sender, src)

            tasks.append(marked)

            self.write_list(tasks, sender, current)

            return self.feedback(_("Changed mark on task '%s'") % marked[4:],
                sender, src)

        except IndexError:
            return self.feedback(_("Task %s does not exist") % task_num,
                sender, src)

    @Message(tags=["remove-list"])
    def remove_list(self, tlist, sender, src):
        """ Remove the specified list. """
        self.set_locale(sender)

        if not self.list_exists(sender, tlist):
            return self.feedback(MSG_LIST_NOT_EXIST, sender, src)

        list_path = path(TODO_PATH, sender, tlist)

        os.remove(list_path)

        current = self.get_current(sender)
        if current == tlist:
            self.set_current(sender, "")

        return self.feedback(_("Removed list '%s'") % tlist, sender, src)

    @Message(tags=["remove-task"])
    def remove_task(self, task_num, sender, src):
        """ Remove a task from the current list. """
        self.set_locale(sender)

        current = self.get_current(sender)

        if not current:
            return self.feedback(MSG_CURRENT_NOT_FOUND, sender, src)

        if not self.list_exists(sender, current):
            return self.feedback(MSG_LIST_NOT_EXIST, sender, src)

        tasks = self.read_list(sender, current)

        try:
            tasks.pop(int(task_num))

            self.write_list(tasks, sender, current)

            return self.feedback(_("Removed task %s") % task_num, sender, src)

        except IndexError:
            return self.feedback(_("Task %s does not exist") % task_num,
                sender, src)

    @Message(tags=["show-lists"])
    def show_lists(self, sender, src):
        """ Show all the list available to the user. """
        self.set_locale(sender)

        user_dir = path(TODO_PATH, sender)
        current = self.get_current(sender)

        if not os.path.isdir(user_dir):
            return self.feedback(MSG_NO_LISTS, sender, src)

        msg = ""
        for d in os.listdir(user_dir):
            if d == current:
                msg += "-> %s\n" % d
            else:
                msg += "%s\n" % d

        if not msg:
            msg = MSG_NO_LISTS

        return self.feedback(msg, sender, src)

    @Message(tags=["show-tasks"])
    def show_tasks(self, sender, src, tlist=None):
        """ Show tasks in the specified list.

            If no list is specified, show in current list.
        """
        self.set_locale(sender)

        if not tlist:
            current = self.get_current(sender)

            if not current:
                return self.feedback(MSG_CURRENT_NOT_FOUND, sender, src)

            if not self.list_exists(sender, current):
                return self.feedback(MSG_LIST_NOT_EXIST, sender, src)

        else:
            current = tlist

        tasks = self.read_list(sender, current)

        msg = ""
        for index, task in enumerate(tasks):
            msg += "%d.- %s\n" % (index, task)

        if not msg:
            msg = _("There are no tasks")

        msg = _("Tasks in list '%s'\n-------\n") % current + msg

        return self.feedback(msg, sender, src)

    def check_dir(self, user):
        """ Check if the user has a directory inside the todo tree and
            create it if it is not present.
        """
        user_path = path(TODO_PATH, user)

        if not os.path.isdir(user_path):
            os.mkdir(user_path)

    def feedback(self, message, user, dst):
        """ Send a feedback message to the user through Jabber.

            message - message to send
            user    - user to send the message to. User is obtained from the
                natural language script.
            dst     - medium to send the message through ('jabber' or 'tg')
        """
        to_send = {
            "dst": "relay",
            "relayto": dst,
            "to": user,
            "msg": message
        }

        return zoe.MessageBuilder(to_send)

    def get_current(self, user):
        """ Read the configuration file with the current lists and
            return the name of the current list for the user.

            If no list is found, return None.
        """
        conf = ConfigParser()
        conf.read(TODO_CURRENT)

        if user not in conf.sections():
            return None

        return conf[user]["current"]

    def list_exists(self, user, tlist):
        """ Determine whether the specified list exists for the given
            user or not.
        """
        list_path = path(TODO_PATH, user, tlist)

        if not os.path.isfile(list_path):
            return False

        return True

    def read_list(self, user, tlist):
        """ Read the list for the specified user line by line and return
            all the tasks.
        """
        list_path = path(TODO_PATH, user, tlist)

        with open(list_path, "r") as ulist:
            tasks = ulist.read().splitlines()

        return tasks

    def set_current(self, user, new_current):
        """ Set new currently active list for the specified user. """
        conf = ConfigParser()
        conf.read(TODO_CURRENT)

        if user not in conf.sections():
            conf.add_section(user)

        conf[user]["current"] = new_current

        with open(TODO_CURRENT, "w") as list_file:
            conf.write(list_file)

    def set_locale(self, user):
        """ Set the locale for messages based on the locale of the sender.

            If no locale is provided, Zoe's default locale is used or
            English (en) is used by default.
        """
        if not user:
            locale = ZOE_LOCALE

        else:
            conf = Users().subject(user)
            locale = conf.get("locale", ZOE_LOCALE)

        lang = gettext.translation("todo", localedir=LOCALEDIR,
            languages=[locale,])

        lang.install()

    def write_list(self, tasks, user, tlist):
        """ Write back a list of tasks to the specified list.

            The tasks are alphabetically sorted before stored in the list.
        """
        list_path = path(TODO_PATH, user, tlist)

        with open(list_path, "w") as ulist:
            for task in sorted(tasks):
                ulist.write("%s\n" % task)
