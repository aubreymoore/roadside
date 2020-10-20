import sys
import os

py3k = sys.version_info[0] >= 3


class FileList:
    """
    Utility to work with files obtained from a certain directory.
    Formatters allow you to format the file names. They are functions take a string argument and return a string.
    """
    def __init__(self, *formatters):
        if formatters is None:
            formatters = []

        self.formatters = formatters

    @classmethod
    def relative_path(cls, root=None):
        """
        Create a FileList where it formats files so only the name relative to the passed in root is output.
        :param root:
        :return:
        """
        if root is None:
            root = os.getcwd()

        root_length = len(root) + 1  # +1 for leading forward slash

        return cls(lambda path: path[root_length:])

    def _invoke_formatters(self, path):
        for formatter in self.formatters:
            path = formatter(path)

        return path

    def generate_files(self, path=None, skip_hidden=True):
        if path is None:
            path = os.getcwd()
        else:
            path = os.path.expanduser(path)

        for root, subdirs, files in os.walk(path):
            if skip_hidden:
                files = [f for f in files if not f[0] == '.']
                subdirs[:] = [d for d in subdirs if not d[0] == '.']

            for name in files:
                raw_path = os.path.join(root, name)
                formatted_path = self._invoke_formatters(raw_path)

                yield formatted_path


if py3k:
    def get_file_tree(path, skip_hidden=True):
        """
        Finds all files in the specified path and subdirectories.

        :param path:
        :type path str
        :return: a map with key being the file path and value being the statistics of the file
        """

        result = []

        for root, subdirs, files in os.walk(path):
            if skip_hidden:
                files = [f for f in files if not f[0] == '.']
                subdirs[:] = [d for d in subdirs if not d[0] == '.']

            for name in files:
                result.append(os.path.join(root, name))

        return result
else:
    def get_file_tree(path, skip_hidden=True):
        """
        Finds all files in the specified path and subdirectories.

        :param path:
        :type path str
        :return: a map with key being the file path and value being the statistics of the file
        """

        result = []

        for root, subdirs, files in os.walk(path):
            if skip_hidden:
                files = [f for f in files if not f[0] == '.']
                subdirs[:] = [d for d in subdirs if not d[0] == '.']

            for name in files:
                file_path = os.path.join(root, name)
                file_path = file_path.decode('utf-8')

                result.append(file_path)

        return result


def generate_file_tree(path, skip_hidden=True):
    """
    Finds all files in the specified path and subdirectories, yields them one at a time.

    :param path:
    :type path str
    :param skip_hidden
    :type bool
    :return: a map with key being the file path and value being the statistics of the file
    """

    for root, subdirs, files in os.walk(path):
        if skip_hidden:
            files = [f for f in files if not f[0] == '.']
            subdirs[:] = [d for d in subdirs if not d[0] == '.']

        for name in files:
            yield os.path.join(root, name)
