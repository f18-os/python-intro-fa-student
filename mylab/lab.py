#! /usr/bin/env python3

import os, sys, time, re

pid = os.getpid()               # get and remember pid
PS1 = "test $ "
PWD = os.environ['PWD']
command = ['null']
exit = False

while not exit:
    command = input(PS1).split()
    if len(command) == 0:
        command = [' ']
    elif command[0] == "exit":
        exit = True
        break

    args = command[0:]
    os.write(1, ("About to fork (pid=%d)\n" % pid).encode())

    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:                   # child
        os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                     (os.getpid(), pid)).encode())

        os.close(1)                 # redirect child's stdout

        #redirect
        redirect = "p4-output.txt"
        for index, arg in enumerate(args):
            if arg == '>':
                redirect = args[index + 1]
                args.remove(args[index+1]) #remove file name
                args.remove(arg)    #remove >


        sys.stdout = open(redirect, "w")
        fd = sys.stdout.fileno() # os.open("p4-output.txt", os.O_CREAT)
        os.set_inheritable(fd, True)
        os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())



        for dir in re.split(":", os.environ['PATH']): # try each directory in path
            program = "%s/%s" % (dir, command[0])

            #os.write(2, ("test print %s\n" % program).encode())

            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                print("error")
                pass                              # ...fail quietly 

        os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                 # terminate with error

    else:                           # parent (forked ok)
        os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                     (pid, rc)).encode())
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                     childPidCode).encode())

