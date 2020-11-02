import os
import errno
import sys
from shutil import copyfile


def get_tab_list(tab_string):
    return [x.rstrip() for x in tab_string.split("\n") if x.strip()]


def get_tab_size(tab_list):
    # first detected intendation is set as tab_size (or 1)
    tab_size = 1
    for line in tab_list:
        tab_size = len(line) - len(line.lstrip())
        if tab_size:
            break

    # basic sanity checks
    last_line_whitespace = 0
    for i, line in enumerate(tab_list):
        whitespace = len(line) - len(line.lstrip())
        # check for jumps greater than one level
        if whitespace > last_line_whitespace + tab_size:
            print("'{}' contains nonmanifold tabstructure.".format(tabbedFile))
            print("Line {} jumps more than one folderlevel.".format(i + 1))
            print("No folders created.")
            return
        # check for jumps that are no multiple of "tab_size"
        tab_mod = whitespace % tab_size
        if not(tab_mod == 0 or tab_mod == tab_size):
            print("'{}' contains nonmanifold tabstructure.".format(tabbedFile))
            print("Line {} has mismatching intendation level.".format(i + 1))
            print("No folders created.")
            return
        last_line_whitespace = whitespace
        # TODO: check for same named dirs on same level
    return tab_size


def get_creation_list(tab_string="", destination="", template_dir="templates"):
    # basic parameter sanity cheks
    if not destination:
        print("No destination specified. Aborted.")
        return
    else:
        if not os.path.isdir(destination):
            print("Destination directory does not exist.")
            return
    if not os.path.isdir(template_dir):
        print("Template directory '{}' does not exist.".format(template_dir))
        print("Files will be created as emtpy textfiles.")

    tab_list = get_tab_list(tab_string)
    tab_size = get_tab_size(tab_list)

    # parsing
    creation_dirs = []
    seen_orig = []
    seen = []
    path = []

    for line in tab_list:
        foldername = line.lstrip()
        depth = int((len(line) - len(foldername)) / tab_size)
        source_file = foldername
        if "<<" in foldername:
            foldername, source_file = foldername.replace(" ", "").split("<<")
        path = path[:depth]      # shorten the path-list down to the correct level
        path.append(foldername)  # and append the current folder
        path_string = os.path.normpath(os.path.join(destination, *path))
        seen_orig.append(path_string)
        if path_string in seen:
            path_string += "_{}".format(seen_orig.count(path_string))
        seen.append(path_string)

        src = ""
        if os.path.isfile(os.path.join(template_dir, source_file)):
            src = os.path.join(template_dir, source_file)

        creation_dirs.append({
            "path": path_string,
            "is_dir": "." not in foldername,
            "source_file": src 
        })

    return creation_dirs

        
def make_from_list(dir_folder_list, simulate=False):
    for dir_folder in dir_folder_list:
        if dir_folder["is_dir"]:
            if simulate:
                print("Creating directory '{}'.".format(dir_folder["path"]))
            else:
                os.mkdir(dir_folder["path"])
        else:
            if dir_folder["source_file"]:
                if simulate:
                    print("Copy '{}' to '{}'.".format(
                        dir_folder["source_file"], dir_folder["path"]
                    ))
                else:
                    copyfile(dir_folder["source_file"], dir_folder["path"])
            else:
                if simulate:
                    print("Creating empty textfile '{}'".format(dir_folder["path"]))
                else:
                    f = open(dir_folder["path"], "w")
                    f.close()


def folders_from_string(tab_string, destination="", template_dir="templates", simulate=False):
    mk_list = get_creation_list(tab_string, destination, template_dir)
    make_from_list(mk_list, simulate)


def silent_remove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred


def silent_rename(old_name, new_name):
    try:
        os.rename(old_name, new_name)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred
