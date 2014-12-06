#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Zoe Agent Manager - https://github.com/RMed/zoe_agent_manager
#
# Copyright (c) 2014 Rafael Medina García <rafamedgar@gmail.com>
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

import os
import zoe
from configparser import ConfigParser
from os import environ as env
from os.path import join as path
from zoe.deco import *

TODO_CURRENT = path(env["ZOE_HOME"], "etc", "current_todo.conf")
TODO_PATH = path(env["ZOE_HOME"], "etc", "todo")


@Agent(name="todo")
class Todo:

    @Message(tags=["add-task"])
    def add_task(self, user, task):
        """ Add a task to current list. """
        current = self.read_current(user)

        if not current:
            msg = "Did not find current active list"
            print(msg)
            return self.feedback(user, msg)

        if not self.list_exists(user, current):
            msg = "List does not exist"
            print(msg)
            return self.feedback(user, msg)

        tasks = self.read_list(user, current)

        tasks.append(task)

        self.write_list(tasks, user, current)

        return self.feedback(user, "Added task '%s' to list" % task)

    @Message(tags=["change-current"])
    def change_current(self, user, new_current):
        """ Change currently active list for the user.

            If the list does not exist, it will be created.
        """
        list_path = path(TODO_PATH, user, new_current)

        if not os.path.isfile(list_path):
            with open(list_path, "w"):
                pass

        self.set_current(user, new_current)

        return self.feedback(user, "Changed to list '%s'" % new_current)

    @Message(tags=["create-list"])
    def create_list(self, user, new_list):
        """ Create a new empty list.

            If the list already exist, creation will be cancelled.
        """
        list_path = path(TODO_PATH, user, new_list)

        if os.path.isfile(list_path):
            msg = "List '%s' already exists" % new_list
            print(msg)
            return self.feedback(user, msg)

        with open(list_path, "w"):
            pass

        msg = "Created new list '%s'" % new_list
        print(msg)
        return self.feedback(user, msg)

    @Message(tags=["mark"])
    def mark_task(self, user, task_num, mark):
        """ Mark or unmark a given task in current list.

            The task is searched by index number.
        """
        current = self.read_current(user)

        if not current:
            msg = "Did not find current active list"
            print(msg)
            return self.feedback(user, msg)

        if not self.list_exists(user, current):
            msg = "List does not exist"
            print(msg)
            return self.feedback(user, msg)

        tasks = self.read_list(user, current)

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
                msg = "Mark not recognized"
                print(msg)
                return self.feedback(user, msg)

            tasks.append(marked)

            self.write_list(tasks, user, current)

            msg = "Changed mark on task %s" % task_num
            print(msg)
            return self.feedback(user, msg)

        except IndexError:
            msg = "Task %s does not exist" % task_num
            print(msg)
            return self.feedback(user, msg)

    @Message(tags=["show-lists"])
    def show_lists(self, user):
        """ Show all the list available to the user. """
        user_dir = path(TODO_PATH, user)

        if not os.path.isdir(user_dir):
            msg = "There are no lists"
            print(msg)
            return self.feedback(user, msg)

        msg = "\n".join(os.listdir(user_dir))
        return self.feedback(user, msg)

    @Message(tags=["show-tasks"])
    def show_tasks(self, user, tlist=None):
        """ Show tasks in the specified list.

            If no list is specified, show in current list.
        """
        if not tlist:
            current = self.get_current(user)

            if not current:
                msg = "Did not find current active list"
                print(msg)
                return self.feedback(user, msg)

            if not self.list_exists(user, current):
                msg = "List does not exist"
                print(msg)
                return self.feedback(user, msg)

        else:
            current = tlist

        tasks = self.read_list(user, current)

        msg = ""
        for index, task in enumerate(tasks):
            msg += index + ".- " + task + "\n"

        return self.feedback(user, msg)

    @Message(tags=["remove-list"])
    def remove_list(self, user, tlist):
        """ Remove the specified list. """
        list_path = path(TODO_PATH, user, tlist)
        if not self.list_exists(user, current):
            msg = "List does not exist"
            print(msg)
            return self.feedback(user, msg)

        list_path = path(TODO_PATH, user, tlist)

        os.remove(list_path)

        msg = "Removed list '%s'" % tlist
        print(msg)
        return self.feedback(user, msg)

    @Message(tags=["remove-task"])
    def remove_task(self, user, task_num):
        """ Remove a task from the current list. """
        current = self.read_current(user)

        if not current:
            msg = "Did not find current active list"
            print(msg)
            return self.feedback(user, msg)

        if not self.list_exists(user, current):
            msg = "List does not exist"
            print(msg)
            return self.feedback(user, msg)

        tasks = self.read_list(user, current)

        try:
            tasks.pop(int(task_num))

            self.write_list(tasks, user, current)

            msg = "Removed task %s" % task_num
            print(msg)
            return self.feedback(user, msg)

        except IndexError:
            msg = "Task %s does not exist" % task_num
            print(msg)
            return self.feedback(user, msg)

    def feedback(self, user, message):
        """ Send a feedback message to the user through Jabber.

            user -- user to send the message to. User is obtained from the
                natural language script.
            message -- message to send
        """
        to_send = {
            "dst": "relay",
            "tag": "relay",
            "relayto": "jabber",
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

    def write_list(self, tasks, user, tlist):
        """ Write back a list of tasks to the specified list.

            The tasks are alphabetically sorted before stored in the list.
        """
        list_path = path(TODO_PATH, user, tlist)

        with open(list_path, "w") as ulist:
            ulist.writelines(sorted(tasks))
