import os
import concurrent.futures
import threading

from onepanel.utilities.s3.wrapper import Wrapper as S3Wrapper
from onepanel.utilities.python_bridge import computer_cpu_count


class ThreadsafeGenerator:
    """Takes an generator and makes it thread-safe by
    wrapping the call to next with a lock."""
    def __init__(self, generator):
        self.generator = generator
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def next(self):
        with self.lock:
            return next(self.generator)


class AtomicInteger:
    def __init__(self, value=0):
        self._value = value
        self._lock = threading.Lock()

    @property
    def value(self):
        with self._lock:
            return self._value

    def increase(self, amount=1):
        with self._lock:
            self._value += amount

    def decrease(self, amount=1):
        self.increase(-amount)


class SourceFuture:
    def __init__(self,  future, source):
        self.future = future
        self.source = source
        self._done_callbacks = []
        self.future.add_done_callback(self.on_done)

    def add_done_callback(self, fn):
        if not self.future.done():
            self._done_callbacks.append(fn)
            return

        fn(self.source, self.future)

    def on_done(self, result):
        for callback in self._done_callbacks:
            callback(self.source, result)


class FileActionResult:
    def __init__(self, key, action):
        self.key = key
        self.action = action

    def __str__(self):
        return '{}: {}'.format(self.action, self.key)


class S3Uploader:
    """
    Issues:
     * User cancels upload (ctrl + c). Doesn't immediately stop.

    """
    def __init__(self, s3_wrapper, workers=None, upload_threads=None):
        """

        :param s3_wrapper:
        :type s3_wrapper S3Wrapper
        :param workers: Number of threads to upload files. If we have 1 thread, we upload 1 file at a time. 5 threads,
                        5 files at a time.

                        Defaults to cpu count * 10

        :param upload_threads: Number of threads per file upload. If we have 5 threads, we can use up to 5 threads to
                               upload a single file.

                               Defaults to cpu count * 10
        """
        self.s3_wrapper = s3_wrapper

        if workers is None:
            workers = (computer_cpu_count() or 1) * 10

        if upload_threads is None:
            upload_threads = (computer_cpu_count() or 1) * 10

        self.upload_threads = upload_threads
        self._active = True
        self.callbacks = []
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
        self._current_uploads = AtomicInteger()
        self._max_uploads = workers * 2
        self.stop_flag = threading.Event()

        self.file_paths = None
        self.to_directory = None
        self.files_uploaded = 0

    def _format_path(self, path, to_directory):
        """
        Forms to_directory / path.

        Takes care of issues with forward slashes so we have a consistent,
        a/b/c/d/e.

        Note there is no leading slash - per s3 format.

        Also, windows paths with backslashes '\', are converted to forward slashes.

        :param path:
        :param to_directory:
        :return:
        """
        if to_directory[0] == '/':
            to_directory = to_directory[1:]

        if to_directory[-1] != '/':
            to_directory += '/'

        path.replace('\\', '/')

        if path[0] == '/':
            path = path[1:]

        return to_directory + path

    def upload_files(self, file_paths, to_directory='/', *callbacks):
        """

        :param file_paths: a generator of file paths.
        :param to_directory: the s3 path prefix to upload to.
        :param callbacks
        :return:
        """

        if not isinstance(to_directory, str):
            to_directory = str(to_directory)

        self.to_directory = to_directory
        self.file_paths = ThreadsafeGenerator(file_paths)

        if callbacks is not None:
            self.callbacks = callbacks

        self._process_upload()

    def _upload(self, file_path):
        """
        Uploads the file. file_path is uploaded to self.to_directory

        Precondition: self.lock is locked. This is so we can thread-safely increment the _current_uploads
        :param file_path:
        :return:
        """
        self._current_uploads.increase()

        key = self._format_path(file_path, self.to_directory)
        task = self.executor.submit(self.s3_wrapper.upload_file, file_path, key, self.upload_threads)
        source_task = SourceFuture(task, FileActionResult(file_path, 'upload'))

        source_task.add_done_callback(self._done_upload)

        for callback in self.callbacks:
            source_task.add_done_callback(callback)

    def _done_upload(self, source, result):
        self._current_uploads.decrease()
        self.files_uploaded += 1

        self._process_upload()

    def _process_upload(self):
        """
        Submits files to be uploaded. Ensures we do not go over the _max_uploads.

        This request is ignored if the uploader has been shutdown.

        :return:
        """

        if not self._active:
            return

        if self._current_uploads.value >= self._max_uploads:
            return

        while self._current_uploads.value < self._max_uploads:
            try:
                file_path = self.file_paths.next()
            except StopIteration:
                self._active = False
                break
            else:
                self._upload(file_path)

    def shutdown(self, wait=True):
        if not wait:
            self.stop_flag.set()
            self._active = False
            self.executor.shutdown(False)
            return

        while not self.stop_flag.wait(0.1):
            if self._current_uploads.value == 0:
                self.stop_flag.set()

        self.executor.shutdown(False)


class S3CheckUploader(S3Uploader):
    """
    Checks to see if the file is already present remotely.
    If it is, and it is the same, doesn't upload it.
    """
    def __init__(self, s3_wrapper, workers=None, upload_threads=None):
        S3Uploader.__init__(self, s3_wrapper, workers, upload_threads)
        self.existing_files = {}

    def upload_files(self, file_paths, to_directory='/', *callbacks):
        self.existing_files = self.s3_wrapper.list_files(to_directory)

        S3Uploader.upload_files(self, file_paths, to_directory, *callbacks)

    def _upload(self, file_path):
        key = self._format_path(file_path, self.to_directory)

        # Don't upload the file if its the same as the local one.
        # same means: file name and file size are the same.
        if key in self.existing_files:
            remote_size = self.existing_files[key]['Size']
            existing_size = os.path.getsize(file_path)

            if remote_size == existing_size:
                return

        S3Uploader._upload(self, file_path)


class S3Facade:
    def __init__(self, s3_wrapper, max_threads=None, skip_duplicate_files=True):
        """
        :param s3_wrapper:
        :type s3_wrapper S3Wrapper
        :param max_threads the maximum number of threads to allow per operation. Defaults to (cpu count or 1) * 10
        :type max_threads int
        """
        self.s3_wrapper = s3_wrapper

        if max_threads is None:
            max_threads = (computer_cpu_count() or 1) * 10

        self.max_threads = max_threads
        self._skip_duplicate_files = skip_duplicate_files

    def _format_path(self, path, to_directory):
        """
        Forms to_directory / path.

        Takes care of issues with forward slashes so we have a consistent,
        a/b/c/d/e.

        Note there is no leading slash - per s3 format.

        Also, windows paths with backslashes '\', are converted to forward slashes.

        :param path:
        :param to_directory:
        :return:
        """
        if to_directory[0] == '/':
            to_directory = to_directory[1:]

        if to_directory[-1] != '/':
            to_directory += '/'

        path.replace('\\', '/')

        if path[0] == '/':
            path = path[1:]

        return to_directory + path

    def upload_file(self, file_path, to_directory='/'):
        """

        :param file_path:
        :param to_directory: the s3 path prefix to upload to.
        :return:
        """

        key = self._format_path(file_path, to_directory)
        return self.s3_wrapper.upload_file(file_path, key, max_threads=self.max_threads)

    def upload_files(self, file_paths, to_directory='/', *callbacks):
        """

        :param file_paths:
        :param to_directory: the s3 path prefix to upload to.
        :param callbacks
        :return:
        """

        if not isinstance(to_directory, str):
            to_directory = str(to_directory)

        if self._skip_duplicate_files:
            uploader = S3CheckUploader(self.s3_wrapper)
        else:
            uploader = S3Uploader(self.s3_wrapper)

        uploader.upload_files(file_paths, to_directory, *callbacks)
        return uploader

    def delete_not_in(self, paths, to_directory='/', *callbacks):
        """

        :param paths:
        :param  to_directory: the s3 path prefix to delete from.
        :return:
        """
        remote_files = self.s3_wrapper.list_files(to_directory)
        files_to_delete = remote_files.copy()

        for path in paths:
            formatted_path = self._format_path(path, to_directory)

            if formatted_path in remote_files:
                del files_to_delete[formatted_path]

        for key, value in files_to_delete.items():
            self.s3_wrapper.delete_file(key)

            if callbacks is not None:
                for callback in callbacks:
                    callback(FileActionResult(key, 'deleted'))
