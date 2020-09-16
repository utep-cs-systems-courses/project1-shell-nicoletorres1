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

    else:
        childPid = os.wait()  # wait for child to fork


def redirectOut(args):
    fileIndex = args.index('>') + 1  # check for index of ouput '>'
    fileName = args[fileIndex]  # array index from user input

    args = args[:fileIndex - 1]

    pid = os.getpid()  # get pid

    rc = os.fork()  # ready to fork

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:
        os.close(1)
        sys.stdout = open(fileName, "w")  # open and write to output
        os.set_inheritable(1, True)

        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ)
            except FileNotFoundError:
                pass
            else:
                for dir in re.split(":", os.environ['PATH']):  # check for environment variables
                    program = "%s/%s" % (dir, args[0])
                    try:
                        os.execve(args[0], args, os.environ)
                    except FileNotFoundError:
                        pass

                os.write(2, ("%s: command not found\n" % args[0]).encode())
                sys.exit(1)
    else:
        childPid = os.wait()


def redirectIn(args):
    pid = os.getpid()  # get pid

    rc = os.fork()  # ready to fork

    if rc < 0:  # return error message if fork fails
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:
        del args[1]
        fd = sys.stdout.fileno()  # set file descriptor output

        try:
            os.execve(args[0], args, os.environ)  # execute program
        except FileNotFoundError:
            pass
        for dir in re.split(":", os.environ['PATH']):  # check for environment variables
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass
        os.write(2, ("%s: command not found\n" % args[0]).encode())  # if the command was not found return error
        sys.exit(1)

    else:
        childPid = os.wait()


def pipe(args):
    pid = os.getpid()  # get pid

    pipe = args.index("|")  # check for pipe in command

    pr, pw = os.pipe()  # pipe read(input) pipe write(output)
    for f in (pr, pw):
        os.set_inheritable(f, True)

    rc = os.fork()  # ready to fork

    if rc < 0:
        print("fork failed, returning %d\n" % rc, file=sys.stderr)
        sys.exit(1)

    elif rc == 0:  # write to pipe from child
        args = args[:pipe]

        os.close(1)

        fd = os.dup(pw)  # duplicate file descriptor output
        os.set_inheritable(fd, True)
        for fd in (pr, pw):
            os.close(fd)
        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ)  # try to execute program
            except FileNotFoundError:
                pass
        else:
            for dir in re.split(":", os.environ['PATH']):  # Check for environment variables
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ)  # try to execute program
                except FileNotFoundError:
                    pass

        os.write(2, ("%s: command not found\n" % args[0]).encode())

        sys.exit(1)

    else:
        args = args[pipe + 1:]

        os.close(0)

        fd = os.dup(pr)  # duplicate file descriptor for output
        os.set_inheritable(fd, True)
        for fd in (pw, pr):
            os.close(fd)  # close file descriptor

        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ)  # execute program
            except FileNotFoundError:
                pass
        else:
            for dir in re.split(":", os.environ['PATH']):  # Check for environment variables
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ)  # execute program
                except FileNotFoundError:
                    pass

        os.write(2, ("%s: command not found\n" % args[0]).encode())  # return error if command was not found

        sys.exit(1)


while True:
    print("$", end=" ")  # so it doesn't make a new line
    if 'PS1' in os.environ:  # check and add prompt string to shell
        os.write(1, os.environ['PS1'].encode())
    try:
        userInput = input()  # Get user input
    except EOFError:
        sys.exit(1)
    except ValueError:
        sys.exit(1)

    args = userInput.split()  # Split user input into array

    if "exit" in userInput:  # Exit command
        sys.exit(0)

    if "cd" in args[0]:  # Change directories
        try:
            os.chdir(args[1])  # change directory
        except FileNotFoundError:
            os.write(1, ("cd: %s: No such file or directory\n" % args[1]).encode())
            pass

    elif "|" in userInput:  # Handle pipe
        pipe(args)

    # if  ">" in userInput: # Handle redirection output
    #     redirectOut(args)

    elif "<" in userInput:  # Handle redirection input
        redirectIn(args)

    else:
        fork(args)  # Handle commands

