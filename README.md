zoe-todo
========

Let Zoe manage your task lists.

List structure
--------------

List files follow a very simple structure in which each line represents a task and the tasks have a mark at the beginning on the line indicating whether the task has been done or not. For instance:

```
[ ] Buy food
[ ] Dominate the world
[ ] Walk the dog
[X] Phone Mom
```

In this list, there are three tasks that are not checked/done (`Buy food`, `Dominate the world` and `Walk the dog`), while one other task has been checked/completed (`Phone mom`).

Also note that tasks are automatically ordered alphabetically and that the checked tasks are always below the unchecked ones.

Where are my lists?
-------------------

The agent stores lists inside directories in the path `etc/todo/USER`, where `USER` is the user identification in the Zoe configuration file. This way, a single user may have several lists in their directory and change between them easily.


