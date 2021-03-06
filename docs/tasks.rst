The Tasks
=========

It's a list of tasks basically meaning a shell as Bash script or runnning
inside a Docker container. Tasks can be **ordered** or **parallel**.

Ordered tasks
-------------

Ordered tasks can written as ``- tasks:`` or as ``- tasks(ordered):``
(the way you prefer). It means the same: one shell script is executed after the other:

 ::

    - tasks(ordered):
        - shell:
            script: echo "hello world one!"
        - shell:
            script: echo "hello world two!"

Parallel tasks
--------------
All tasks are running in parallel as much as possible. The
Python module **multiprocessing** is used.

 ::

    - tasks(parallel):
        - shell:
            script: echo "hello world one!"
        - shell:
            script: echo "hello world two!"

**Please note**:
 - It's not a good idea to interrupt the pipeline with Ctrl-C
   because multiprocessing is used.
 - Example: When you have 4 cpus but more than 4 tasks it might happen
   that the tasks do not finish in time constraints as you expect. It
   seems that one task is assigned to one cpu only at a time.
 - When one task fails the pipeline stops after all tasks has been
   finished.
 - When using multiple enviroment blocks tasks run in parallel only
   between two of those "env" blocks.

Environment variables
---------------------
Besides a tasks the list also may contain one or more blocks for environment variables.

::

    - env:
        a: "hello"
        b: "world"

The last block overwrites the previous one; existing variables
are overwriten, new ones are added.

Variables on tasks
------------------
On shells, python scripts and docker container tasks you can specify a variable and
variables are stored at pipeline level. When a block of parallel tasks start all
variables before this time are passed to the tasks and while those are running new
variables cannot be evaluated. But a tasks block also may contain **env** entries
so you can split parallel tasks in two (or more) blocks. Each new block is able
to access last stored variables; here a rough example:

::

    - tasks(parallel):
        # first block
        - shell:
            script: echo "hello"
            variable: one
        - shell:
            script: echo "world"
            variable: two

        - env:
            message: "a great"

        # second block
        - shell:
            script: echo "{{ env.message }} {{ variables.one }} {{ variables.two }}"
        - shell:
            script: echo "{{ env.message }} {{ variables.one }}"
        - shell:
            script: echo "{{ env.message }} {{ variables.two }}"

The two commented blocks are executed in order because of an **env** entry inbetween
but all tasks of one block are executed in parallel. When executing it looks like following:

::

    $ spline --definition=examples/variables.yaml 2>&1 | grep "great"
    2018-01-22 19:49:44,576 - spline.components.tasks.worker -  | a great world
    2018-01-22 19:49:44,577 - spline.components.tasks.worker -  | a great hello
    2018-01-22 19:49:44,581 - spline.components.tasks.worker -  | a great hello world

When the tasks are ordered a previous variable by a previous task
can be evaluated immediately. 
