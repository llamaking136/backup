#!/usr/local/Cellar/python@3.9/3.9.0_1/bin/python3

## XXX: EDIT TO YOUR INTERPRETER PATH!!

from __future__ import print_function

__version__ = "1.0.3"

"""
This program creates a total backup of all files in a certain root directory,
such as for a healthy and kept computer project.
WARNING: can only backup non-binary files
"""

from sys import argv, stdout, stderr, version_info
from os import listdir, getcwd, chdir, walk, mkdir, makedirs
from os.path import isdir, abspath, join, exists
import datetime
from json import loads, dumps
# from bs4 import UnicodeDammit as uni

github = "https://github.com/llamaking136/backup"

def getEncoding(filename):
    with open(filename, "rb") as file:
        return uni(file.read()).original_encoding

if (version_info.major <= 2): print("fatal error: cannot use Python 2 or lower.", file = stderr); exit(3)

if (not exists(".backup")): mkdir(".backup")
# if (not exists(".backup/backup_info.json")): open(".backup/backup_info.json", "wt").write("{}")

def filecheck(file1, file2):
    f1 = open(file1, "rt")
    f2 = open(file2, "rt")
    if f1.read() != f2.read():
        f1.close()
        f2.close()
        return False
    else:
        f1.close()
        f2.close()
        return True

def _help():
    print(f"""
usage: backup [backup, metaview, cmp, help]

backup is a program that backs up files and can
restore files
basically git but worse

options:
    backup    : backs up the current directory
    metaview  : views backups in the past
    cmp       : compares latest backup to current dir
    help      : shows this help page and exits

github: {github}
""")
    exit(1)

def bytething(num):
    if (num <= 999):
        return str(num) + " bytes"
    elif (num >= 1000 and num <= 999999):
        return str(num / 1000) + " kb"
    elif (num >= 1000000 and num <= 999999999):
        return str(num / 1000000) + " mb"
    elif (num >= 1000000000):#and num < 999999999999):
        return str(num / 1000000000) + " gb"

add_hidden = False
backup_times = []
backups = []
backup_files = dict()

if ("-add_hidden" in argv): add_hidden = True

def getcount(countfor): # TODO: remove, i realized there is a `len` function.
    i = 0
    for _ in countfor:
        i += 1
    return i

def remove_comments(data, comment):
    return data.split(comment)[0].strip()
    """
    try:
        if split[-1] == " ":
            return split[0:len(split) - 1]
        else:
            return split
    except IndexError:
        return ""
    """

def readFromBin(filename):
    result = ""#b""
    with open(filename, "r", encoding = "utf-8", errors = "ignore") as f:
        while (byte := f.read(1)):
            result += byte
    return result#.decode(getEncoding(filename))

bak = None
file_list = []
root = getcwd()
dirs = []
try:
    ignore = open(".backignore").read().split("\n")
    for i in range(len(ignore)):
        ignore[i] = remove_comments(ignore[i], "#")
except FileNotFoundError:
    ignore = []

class File:
    def __init__(self, filename, data):
        self.filename = filename
        self.data = data
    def __repr__(self):
        return "File('" + self.filename + "', '" + self.data + "')"

class Backup:
    def __init__(self, time, files, dirs, message):
        self.time = time
        self.files = files
        self.dirs = dirs
        self.message = message

def parse_file(data):
    pass

def index():
    files = []
    dirs = []
    for r, o, t in walk(root):
        for file in t:
            files.append(get_file_path(join(r, file)))
        for dir_ in o:
            dirs.append(get_file_path(join(r, dir_)))
    return files, dirs

def file_index(filenames):
    result = []
    for i in filenames:
        result.append((i, get_file_data(i)))
    return result

def get_file_data(filename):
    try:
        return open(filename, "rt").read()
    except:
        return None

def get_all_files():
    for subdir, dirs, files in walk(root):
        for file in files:
            file_list.append(abspath(join(subdir, file)))

def checkDirs():
    final = []
    for _, dirs, _ in walk(root):
        for i in dirs:
            if i not in final:
                final.append(i)
    return final

def get_file_path(filename):
    return filename[len(root) + 1:]

def add_root_path(filename):
    return root + "/" + filename

def start_backup():
    bak.write("[BACKUP]::[BAK_BEGIN " + str(datetime.date.today()) + " " + str(datetime.datetime.now().time())[0:8] + "]\n")

def backup_file(path, data):
    bak.write("[FILE]::[FILE_BEGIN " + path + "]\n")
    bak.write(data)
    bak.write("\n[FILE]::[FILE_END]\n")

def findDirs(contents):
    final = []
    for i in contents:
        if i.startswith("[DIR]::[NEW_DIR "):
            final.append(i[16:len(i) - 1])
    return final

def backup_dir(path):
    bak.write("[DIR]::[NEW_DIR " + path + "]\n")

def backup_message(message):
    bak.write("[BACKUP]::[MSG %s]\n" % message)

def end_backup():
    bak.write("[BACKUP]::[BAK_END]\n")

def restore_backup(backup):
    print("restoring backup...")
    for i in backup.dirs:
        if exists(i):
            print("warning: dir " + i + " exists, no creation", file = stderr)
            continue
        else:
            print("\33[32mcreating\33[0m dir " + i)
            makedirs(i, exist_ok = True)

    for i in backup.files:
        if exists(i[0]):
            print("warning: file " + i[0] + " exists, overwriting", file = stderr)
            file = open(i[0], "w")
            file.write(i[1])
            file.close()
        else:
            print("\33[32mcreating & writing\33[0m file " + i[0])
            file = open(i[0], "w")
            file.write(i[1])
            file.close()

    print("backup restored with no errors")

def backup():
    total_size = 0
    file_list, dir_list = index()

    current_message = input("backup message (leave blank to abort) > ")
    if not current_message:
        print("aborting")
        exit(1)
    else:
        backup_message(current_message)

    start_backup()

    for i in dir_list:
        print("\33[32mdir\33[0m    " + i + "/")
        backup_dir(i)

    for i in file_list:
        current_file = i.split("/")[-1]
        # print(add_hidden)
        if (current_file[0] == "."):
            continue
        if (current_file == "backup.bak"):
            continue
        if (current_file in ignore):
            # print("\33[35mignore\33[0m " + get_file_path(i))
            continue
        # i = get_file_path(i)
        # path = i.split("/")
        # path.pop(-1)
        # path = "/".join(path)
        # if (path not in dirs and path != ""):
            # if (path in ignore):
            #     print("warning: directory in ignore, ignoring ignore blah blah blah reeeee", file = stderr)
        #     if (path in ignore):
        #         continue
        #     print("\33[32mdir\33[0m    " + path + "/")
        #     dirs.append(path)
        #     backup_dir(path)
                
        print("\33[32madding\33[0m " + i)
        try:
            current_open = open(i).read()
        except UnicodeDecodeError:
            # try:
            # current_open = readFromBin(i)#.decode("windows-1254")#"utf-8", "backslashreplace")
            # except Exception as e:
            #     print("error: cannot open file '" + i + "' for reading, " + str(e), file = stderr)
            #     continue
            print("warning: cannot compile binary file, not yet supported, ignoring", file = stderr)
            continue
        except (PermissionError, IOError):
            print("warning: cannot open file for reading, ignoring", file = stderr)
            continue

        total_size += len(current_open)
        if (not "-no-backups" in argv):
            backup_file(i, current_open)

    end_backup()
    print("total size of all files: " + bytething(total_size))

def ret_backup():
    global backups
    if (not exists(".backup/backup.bak")):
        stderr.write("error: backup file not found\n");stderr.flush()
        exit(1)
    file = open(".backup/backup.bak")
    content = file.read().split("\n")
    file.close()
    line = 0
    back_nums = 0

    back_time = ""
    bace_start = 0
    back_end = 0
    back_content = ""
    back_msg = "(legacy backup)"
    file_start = 0
    file_end = 0
    file_content = ""
    file_list = []
    inBackup = False
    for i in range(len(content)):
        if content[i].startswith("[BACKUP]::[BAK_BEGIN"):
            inBackup = True
            back_start = i
            back_time = content[i][21:40]
            back_nums += 1
        
        if content[i].startswith("[BACKUP]::[BAK_END]"):
            inBackup = False
            back_end = i
            back_content = "\n".join(content[back_start:back_end])
            backups.append(Backup(back_time, file_list, findDirs(content[back_start:back_end]), back_msg))
            file_list = []

        if content[i].startswith("[FILE]::[FILE_BEGIN"):
            file_start = i + 1
            
        if content[i].startswith("[FILE]::[FILE_END]"):
            file_end = i
            file_content = "\n".join(content[file_start:file_end])
            current_filename = content[file_start - 1][20:len(content[file_start - 1]) - 1]
            file_list.append([current_filename, file_content])

        if content[i].startswith("[DIR]::[NEW_DIR "):
            path = content[i][16:len(content[i]) - 1]

        if content[i].startswith("[BACKUP]::[MSG "):
            back_msg = content[i][15:len(content[i]) - 1]

def to_dict(lst):
    result = dict()
    for o, t in lst:
        result[o] = t
    return result

def compare():
    global backups
    ret_backup()
    files_old = []
    dirs_old = []
    for i in backups[-1].files:
        files_old.append((i[0], i[1]))
    for i in backups[-1].dirs:
        dirs_old.append(i)
    files_new, dirs_new = index()
    files_new = file_index(files_new)

    files_new = to_dict(files_new)
    files_old = to_dict(files_old)

    added = []
    deleted = []
    modified = []

    for i in dirs_new: # new vs old dirs
        if i not in dirs_old:
            added.append(i)
    for i in dirs_old:
        if i not in dirs_new:
            deleted.append(i)

    for i in files_new.keys(): # new vs old files
        if i not in files_old.keys():
            added.append(i)
    for i in files_old.keys():
        if i not in files_new.keys():
            deleted.append(i)
    
    # files_new = to_dict(files_new)
    # files_old = to_dict(files_old)

    for i in files_new.keys(): # modified files
        if i in files_old.keys() and files_new[i] != files_old[i]:
            modified.append(i)

    if added:
        print("added files and dirs:")
        for i in added:
            try:
                if i in dirs_new:
                    print("\t\33[32m" + i + "/\33[0m")
                    continue
                print("\t\33[32m" + i + "\33[0m")
            except TypeError:
                print("\t\33[32m" + i[0] + "\33[0m")
    if deleted:
        print("deleted files and dirs:")
        for i in deleted:
            try:
                if i in dirs_old:
                    print("\t\33[31m" + i + "/\33[0m")
                    continue
                print("\t\33[31m" + i + "\33[0m")
            except TypeError:
                print("\t\33[31m" + i[0] + "\33[0m")
    if modified:
        print("modified files:")
        for i in modified:
            print("\t\33[31m" + i + "\33[0m")

    if not added and not deleted and not modified:
        print("nothing changed since last backup")

def get_metadata():
    ret_backup()

    num = 0
    for i in backups:
        num += 1
        print("backup #" + str(num))
        print("time: " + i.time)
        # print("\nfiles: ")
        # for ii in i.files:
        #     print(ii[0])
        # print("\nnew dirs: ")
        # for ii in i.dirs:
        #     print(ii)
        print("message: '%s'" % i.message)
        print()

    try:
        num_what = int(input("which bak to edit? (blank to abort) > "))
        if num_what == "":
            print("aborting")
            exit(1)
        if num_what <= 0 or num_what > num:
            print("error: inputted wrong bak#, stopping", file = stderr)
            exit(1)
    except ValueError:
        print("error: didn't input a number, stopping", file = stderr)
        exit(1)
    num_todo = input(f"what to do to with bak#{num_what}? > ")
    if num_todo == "help":
        print("""commands:
    help - display this help page and exit
    restore - restore a backup to the current directory
    delete - work in progress
    # info - show information on current backup""")
        exit()
    elif num_todo == "restore":
        restore_backup(backups[num - 1])
    elif num_todo == "delete":
        print("error: this is still in a work-in-progress, please check back later", file = stderr)
        exit(1)
    elif num_todo == "files":
        for i in backups[num - 1].files:
            print(i[0])
        exit(1)
    elif num_todo == "dirs":
        for i in backups[num - 1].dirs:
            print(ii)
        exit(1)
    else:
        print("error: unknown command: " + num_todo, file = stderr)
        exit(1)

    file.close()

def restore():
    pass            

if (__name__ == "__main__"):
    try:
        argv[1]
    except IndexError:
        stderr.write("usage: backup [backup, metaview, cmp, help]\n");stderr.flush()
        exit(1)

    if (exists(".backup/backup.bak")):
        bak = open(".backup/backup.bak", "at")
    elif (argv[1].lower() == "backup"):
        bak = open(".backup/backup.bak", "at")
    else:
        stderr.write("fatal error: no backup file found, try backing up\n");stderr.flush()
        exit(1)

    if (argv[1].lower() == "backup"):
        backup()
    elif (argv[1].lower() == "metaview"):
        get_metadata()
    elif argv[1].lower() == "cmp":
        compare()
    elif (argv[1].lower() == "help"):
        _help()
    else:
        stderr.write("error: unknown option: " + argv[1] + "\n");stderr.flush()
        print("if you think this is an error, please report it to my github: " + github, file = stderr)
        exit(1)
