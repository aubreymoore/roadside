import sys

py3k = sys.version_info[0] >= 3

if py3k:
    import os

    def computer_cpu_count():
        return os.cpu_count()

    def make_dirs_if_not_exist(dirname):
        os.makedirs(dirname, exist_ok=True)

else:
    import os
    import multiprocessing

    def computer_cpu_count():
        return multiprocessing.cpu_count()

    def make_dirs_if_not_exist(dirname):
        try:
            os.makedirs(dirname)
        except os.error as exception:
            # exception is raised if some already exist, or can not be created.
            pass
