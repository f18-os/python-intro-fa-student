#! /usr/bin/env python3

import os, sys, time, re

def changeDirectory():
    print("nothing") 

def pipe(left, right):
    os.write(1, (left[0] + " " + right[0] + "\n").encode())
    pr,pw = os.pipe()
    for f in (pr, pw):
        os.set_inheritable(f, True)

    import fileinput


    rc = os.fork()

    if rc < 0:
        sys.exit(1)

    elif rc == 0:                   #  child - will write to pipe
        args = left[0:]
        program = left[0]

        os.close(1)                 # redirect child's stdout
        os.dup(pw)
        for fd in (pr, pw):
            os.close(fd)
        #print("hello from child")
        fd = sys.stdout.fileno()
        execute(program, args)
     
    else:                           # parent (forked ok)
        args = right[0:]
        program = right[0]
        #print("Parent: My pid==%d.  Child's pid=%d" % (os.getpid(), rc), file=sys.stderr)
        os.close(0)
        os.dup(pr)
        execute(program, args)
        for fd in (pw, pr):
            os.close(fd)
        fd = sys.stdin.fileno()
        for line in fileinput.input():
            print("From child: <%s>" % line)

def execute(program, args):
    for dir in re.split(":", os.environ['PATH']): # try each directory in path
        program = "%s/%s" % (dir, command[0])

        try:
            os.execve(program, args, os.environ) # try to exec program
        except FileNotFoundError:             # ...expected
            pass                              # ...fail quietly 

PS1 = ""
if PS1 in os.environ:
    PS1 = os.environ['PS1']
PWD = os.environ['PWD']
command = []
exit = False

while not exit:
    try:
        command = input(PS1)
    except EOFError:
        sys.exit(1)
    if len(command) < 1:
        #command = [' ']
        continue
    elif command == "exit":
        exit = True
        break

    pid = os.getpid()               # get and remember pid

    #os.write(1, ("About to fork (pid=%d)\n" % pid).encode())

    rc = os.fork()
    #r,w = os.pipe()

    if rc < 0:
        #os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:                   # child

        for char in command:
            if char == "|":
                left, right = command.split('|')
                os.write(1, (left + " " + right + "\n").encode())
                pipe(left.split(),right.split())
                command = "nothing"
        #os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
        #             (os.getpid(), pid)).encode())

        #os.close(1)                 # redirect child's stdout
        command = command.split()

        if command[0] == "cd":
            changeDirectory()

        args = command[0:]
        #redirect
        redirect = "p4-output.txt"
        for index, arg in enumerate(args):


            if arg == '>':
                redirect = args[index + 1]
                args.remove(args[index+1]) #remove file name
                args.remove(arg)    #remove >
                os.close(1)

                sys.stdout = open(redirect, "w")
                fd = sys.stdout.fileno() # os.open("p4-output.txt", os.O_CREAT)
                os.set_inheritable(fd, True)
                #os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())

            if arg == '<':
                redirect = args[index + 1]
                args.remove(args[index+1]) #remove file name
                args.remove(arg)    #remove >
                os.close(0)

                sys.stdin = open(redirect, "r")
                fd = sys.stdin.fileno() # os.open("p4-output.txt", os.O_CREAT)
                os.set_inheritable(fd, True)


        for dir in re.split(":", os.environ['PATH']): # try each directory in path
            program = "%s/%s" % (dir, command[0])

            #os.write(2, ("test print %s\n" % program).encode())

            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly 

        #os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                 # terminate with error
    #else:                           # parent (forked ok)
        #os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
        #             (pid, rc)).encode())
      #  childPidCode = os.wait()
        #os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
        #             childPidCode).encode())

