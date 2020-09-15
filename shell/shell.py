#! /usr/bin/env  python3

import os, sys, re


def fork(args):
    pid = os.getpid()  # get and remember pid

    rc = os.fork()  # set rc to fork

    if rc < 0:  # capture error during fork
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:  # child

        fd = sys.stdout.fileno()  # set file descriptor
        os.set_inheritable(fd, True)

        try:
            os.execve(args[0], args, os.environ)  # execute program
        except FileNotFoundError:
            pass
        if "/" in args:
            os.execve(args[0], args, os.environ)

        for dir in re.split(":", os.environ['PATH']):  # check for environment variables
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass

        os.write(2, ("%s: command not found\n" % args[0]).encode())  # if command not found print error
        sys.exit(1)


