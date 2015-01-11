#!/usr/bin/env perl
#
# Zoe Todo - https://github.com/rmed/zoe-todo
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

use Getopt::Long qw(:config pass_through);

my $get;
my $run;
my $add;
my $change;
my $create;
my $mark;
my $remove_list;
my $remove_task;
my $show_lists;
my $show_tasks_current;
my $show_tasks_list;
my $unmark;

my $sender;
my $task_num;
my @strings;

GetOptions("get" => \$get,
           "run" => \$run,
           "msg-sender-uniqueid=s" => \$sender,
           "a" => \$add,
           "ch" => \$change,
           "cl" => \$create,
           "m" => \$mark,
           "rl" => \$remove_list,
           "rt" => \$remove_task,
           "sl" => \$show_lists,
           "st" => \$show_tasks_current,
           "stl" => \$show_tasks_list,
           "um" => \$unmark,
           "integer=s" => \$task_num,
           "string=s" => \@strings);

if ($get) {
  &get;
} elsif ($run and $add) {
  &add;
} elsif ($run and $change) {
  &change;
} elsif ($run and $create) {
  &create;
} elsif ($run and $mark) {
  &mark;
} elsif ($run and $remove_list) {
  &remove_list;
} elsif ($run and $remove_task) {
  &remove_task;
} elsif ($run and $show_lists) {
  &show_lists;
} elsif ($run and $show_tasks_current) {
  &show_tasks_current;
} elsif ($run and $show_tasks_list) {
  &show_tasks_list;
} elsif ($run and $unmark) {
  &unmark;
}


#
# Commands in the script
#
sub get {
  print("--a add /the task <string>\n");
  print("--ch change /the /current list to <string>\n");
  print("--cl create /new list <string>\n");
  print("--m mark /the task <integer>\n");
  print("--rl remove /the list <string>\n");
  print("--rt remove /the task <integer>\n");
  print("--sl show /the lists\n");
  print("--st show /the tasks\n");
  print("--stl show /the tasks in <string>\n");
  print("--um unmark /the task <integer>\n");

  print("--a añade /la tarea <string>\n");
  print("--ch cambia /la lista /actual a <string>\n");
  print("--cl crea /nueva lista <string>\n");
  print("--m marca /la tarea <integer>\n");
  print("--rl elimina /la lista <string>\n");
  print("--rt elimina /la tarea <integer>\n");
  print("--sl muestra /las listas\n");
  print("--st muestra /las tareas\n");
  print("--stl muestra /las tareas en <string>\n");
  print("--um desmarca /la tarea <integer>\n");
}

#
# Add a task to the list
#
sub add {
  print("message dst=todo&tag=add-task&user=$sender&task=$strings[0]\n");
}

#
# Change current list
#
sub change {
  print("message dst=todo&tag=change-current&user=$sender&new_current=$strings[0]\n");
}

#
# Create new list
#
sub create {
  print("message dst=todo&tag=create-list&user=$sender&new_list=$strings[0]\n");
}

#
# Mark a task
#
sub mark {
  print("message dst=todo&tag=mark&user=$sender&task_num=$task_num&mark=1\n");
}

#
# Remove a list
#
sub remove_list {
  print("message dst=todo&tag=remove-list&user=$sender&tlist=$strings[0]\n");
}

#
# Remove a task
#
sub remove_task {
  print("message dst=todo&tag=remove-task&user=$sender&task_num=$task_num\n");
}

#
# Show all lists owned by the user
#
sub show_lists {
  print("message dst=todo&tag=show-lists&user=$sender\n");
}

#
# Show all the tasks in current list
#
sub show_tasks_current {
  print("message dst=todo&tag=show-tasks&user=$sender\n");
}

#
# Show all the tasks in specified list
#
sub show_tasks_list {
  print("message dst=todo&tag=show-tasks&user=$sender&tlist=$strings[0]\n");
}

#
# Unmark a task
#
sub unmark {
  print("message dst=todo&tag=mark&user=$sender&task_num=$task_num&mark=0\n");
}
