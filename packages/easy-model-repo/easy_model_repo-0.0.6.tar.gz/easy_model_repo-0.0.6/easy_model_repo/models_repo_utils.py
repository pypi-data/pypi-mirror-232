import http
import json
import os.path
import uuid
import requests
from minio import Minio
from minio.error import S3Error
import sys
import time
from queue import Empty, Queue
from threading import Thread

_BAR_SIZE = 20
_KILOBYTE = 1024
_FINISHED_BAR = '#'
_REMAINING_BAR = '-'
_UNKNOWN_SIZE = '?'
_STR_MEGABYTE = ' MB'
_HOURS_OF_ELAPSED = '%d:%02d:%02d'
_MINUTES_OF_ELAPSED = '%02d:%02d'
_RATE_FORMAT = '%5.2f'
_PERCENTAGE_FORMAT = '%3d%%'
_HUMANINZED_FORMAT = '%0.2f'
_DISPLAY_FORMAT = '|%s| %s/%s %s [elapsed: %s left: %s, %s MB/sec]'
_REFRESH_CHAR = '\r'

ADMIN_HOST = "dev06.ucd.qzm.stonewise.cn:30022"
MODEL_REPO_BUCKET = "model-repo"


class EasyModelRepo:
    def __init__(self, gateway, key, secret):
        self.client = Minio(
            gateway,
            access_key=key,
            secret_key=secret,
            secure=False,
        )
        self.creator = "lizhengnan"

    def new_model(self, model_name, description, library, data_set, task, maintainers):
        if model_name == "":
            print("Param model_name is empty")
            return
        info = json.dumps({
            'model_name': model_name,
            'description': description,
            'library': library,
            'data_set': data_set,
            'task': task,
            'maintainers': maintainers,
            'creator': self.creator,
        })
        res = self._new_model_req(info)
        print(res.text)

    def get_user_model(self):
        res = self._get_user_model_list_req()
        if res.status_code != http.HTTPStatus.OK:
            print(res.status_code)
            return
        print(res.json().get("data"))

    def get_model_by_tag(self, model_name, tag, destination_path):
        if tag == "":
            print("Param tag is empty")
            return
        if model_name == "":
            print("Param model_name is empty")
            return
        if os.path.isfile(destination_path):
            print("Param destination_path must be a folder")
        res = self._get_tag_storage_path_req(model_name, tag)
        if res.status_code == http.HTTPStatus.BAD_REQUEST:
            print(res.text)
            return
        blob_path = res.json().get("blob_path")
        if os.path.isdir(destination_path):
            objects = self.client.list_objects(
                "model-repo", recursive=True, prefix=blob_path,
            )
            for obj in objects:
                parts = obj.object_name.split('/')
                if len(parts) > 4:
                    full_path = '/'.join(parts[3:])
                else:
                    full_path = ''
                err = self._download(obj.object_name, os.path.join(destination_path, full_path))
                if err != "":
                    return err

            print("Files download successfully.")
        return

    def get_model_by_version(self, model_name, version, destination_path):
        if version == "":
            print("Param version is empty")
            return
        if model_name == "":
            print("Param model_name is empty")
            return
        if os.path.isfile(destination_path):
            print("Param destination_path must be a folder")
        res = self._get_version_storage_path_req(model_name, version)
        if res.status_code == http.HTTPStatus.BAD_REQUEST:
            print(res.text)
            return
        blob_path = res.json().get("blob_path")
        if os.path.isdir(destination_path):
            objects = self.client.list_objects(
                "model-repo", recursive=True, prefix=blob_path,
            )
            for obj in objects:
                parts = obj.object_name.split('/')
                if len(parts) > 4:
                    full_path = '/'.join(parts[3:])
                else:
                    full_path = ''
                err = self._download(obj.object_name, os.path.join(destination_path, full_path))
                if err != "":
                    return err

            print("Files download successfully.")
        return

    def get_model_version_list(self, model_name):
        res = self._get_model_version_list_req(model_name)
        if res.status_code != http.HTTPStatus.OK:
            print(res.status_code)
            return
        print(res.json().get("version_list"))

    def new_model_version(self, model_name, version, tag, local_path):
        if model_name == "":
            print("Param model_name is empty")
            return
        if local_path == "":
            print("Param local_path is empty")
            return
        if tag == "":
            print("Param tag is empty")
            return
        blob_path = ""
        uid = str(uuid.uuid4())
        checkres = self._get_model_id_req(model_name)
        if checkres.status_code == http.HTTPStatus.BAD_REQUEST:
            print(checkres.json().get("msg"))
            return
        if checkres.status_code != http.HTTPStatus.OK:
            print(checkres.status_code)
            return
        if os.path.isfile(local_path):
            folder_name = os.path.basename(os.path.dirname(local_path))
            file_name = os.path.basename(local_path)
            destination_path = "/models/{model_name}/{guid}/{folder_name}/{file_name}".format(model_name=model_name,
                                                                                              guid=uid,
                                                                                              folder_name=folder_name,
                                                                                              file_name=file_name)
            err = self._upload(local_path, destination_path)
            if err != "":
                return
            blob_path = destination_path
            print("File uploaded successfully.")
        elif os.path.isdir(local_path):
            allfiles = _getallfiles(local_path)
            for file in allfiles:
                master_folder_name = os.path.basename(os.path.dirname(local_path))
                file_path = file.split(master_folder_name + '/')[1]
                destination_path = os.path.join('models', model_name, uid, file_path)
                source_path = os.path.join(local_path, file)
                err = self._upload(source_path, destination_path)
                if err != "":
                    return
            blob_path = "/models/{model_name}/{guid}/".format(model_name=model_name, guid=uid)
            print("Files uploaded successfully.")
        else:
            print("Please input right path")

        info = json.dumps({
            'model_name': model_name,
            'tag': tag,
            'blob_path': blob_path,
            'guid': "{guid}".format(guid=uid),
            'version': version
        })
        addres = self._add_model_version_req(info)
        if addres.status_code == http.HTTPStatus.BAD_REQUEST:
            print(addres.json().get("msg"))
            return
        if checkres.status_code != http.HTTPStatus.OK:
            print(checkres.status_code)
            return

    def _upload(self, local_path, destination):
        try:
            self.client.fput_object(
                "model-repo",
                destination,
                local_path,
                progress=Progress(),  # 在回调中调用线程对象的run方法
            )
            print("File uploaded successfully.")
            return ""
        except S3Error as err:
            print("Error: ", err)
            return err

    def _download(self, source, destination):
        try:
            # Download data of an object.
            self.client.fget_object(
                "model-repo",
                source,
                destination,
                progress=Progress(),  # 在回调中调用线程对象的run方法
            )
            return ""
        except S3Error as err:
            print("Error: ", err)
            return err

    def _delete_model_version_req(self, model_name, model_version):
        base_url = "http://{host}/api/v1/model/version/{model_name}/{model_version}" \
            .format(host=ADMIN_HOST, model_name=model_name, model_version=model_version)
        res = requests.delete(url=base_url)
        return res

    def _delete_model_tag_req(self, model_name, model_tag):
        base_url = "http://{host}/api/v1/model/tag/{model_name}/{model_tag}" \
            .format(host=ADMIN_HOST, model_name=model_name, model_tag=model_tag)
        res = requests.delete(url=base_url)
        return res

    def _delete_model_req(self, model_name):
        base_url = "http://{host}/api/v1/model/{model_name}" \
            .format(host=ADMIN_HOST, model_name=model_name)
        res = requests.delete(url=base_url)
        return res

    def _get_model_id_req(self, model_name):
        base_url = "http://{host}/api/v1/model/{model_name}/id" \
            .format(host=ADMIN_HOST, model_name=model_name)
        res = requests.get(url=base_url)
        return res

    def _get_model_info_req(self, model_name):
        base_url = "http://{host}/api/v1/model/{model_name}/info" \
            .format(host=ADMIN_HOST, model_name=model_name)
        res = requests.get(url=base_url)
        return res

    def _get_tag_storage_path_req(self, model_name, model_tag):
        base_url = "http://{host}/api/v1/model/tag/{model_name}/{model_tag}/storage" \
            .format(host=ADMIN_HOST, model_name=model_name, model_tag=model_tag)
        res = requests.get(url=base_url)
        return res

    def _get_version_storage_path_req(self, model_name, model_version):
        base_url = "http://{host}/api/v1/model/version/{model_name}/{model_version}/storage" \
            .format(host=ADMIN_HOST, model_name=model_name, model_version=model_version)
        res = requests.get(url=base_url)
        return res

    def _get_model_version_list_req(self, model_name):
        base_url = "http://{host}/api/v1/model/{model_name}/version/list" \
            .format(host=ADMIN_HOST, model_name=model_name)
        res = requests.get(url=base_url)
        return res

    def _get_user_model_list_req(self):
        base_url = "http://{host}/api/v1/{username}/model/list" \
            .format(host=ADMIN_HOST, username=self.creator)
        res = requests.get(url=base_url)
        return res

    def _add_model_version_req(self, json_info):
        headers = {'Content-Type': 'application/json'}
        base_url = "http://{host}/api/v1/model/version/add".format(host=ADMIN_HOST)
        res = requests.post(url=base_url, data=json_info, headers=headers)
        return res

    def _new_model_req(self, json_info):
        headers = {'Content-Type': 'application/json'}
        base_url = "http://{host}/api/v1/model/init".format(host=ADMIN_HOST)
        res = requests.post(url=base_url, data=json_info, headers=headers)
        return res


class Progress(Thread):
    """
        Constructs a :class:`Progress` object.
        :param interval: Sets the time interval to be displayed on the screen.
        :param stdout: Sets the standard output

        :return: :class:`Progress` object
    """

    def __init__(self, interval=1, stdout=sys.stdout):
        Thread.__init__(self)
        self.daemon = True
        self.total_length = 0
        self.interval = interval
        self.object_name = None

        self.last_printed_len = 0
        self.current_size = 0

        self.display_queue = Queue()
        self.initial_time = time.time()
        self.stdout = stdout
        self.start()

    def set_meta(self, total_length, object_name):
        """
        Metadata settings for the object. This method called before uploading
        object
        :param total_length: Total length of object.
        :param object_name: Object name to be showed.
        """
        self.total_length = total_length
        self.object_name = object_name
        self.prefix = self.object_name + ': ' if self.object_name else ''

    def run(self):
        displayed_time = 0
        while True:
            try:
                # display every interval secs
                task = self.display_queue.get(timeout=self.interval)
            except Empty:
                elapsed_time = time.time() - self.initial_time
                if elapsed_time > displayed_time:
                    displayed_time = elapsed_time
                self.print_status(current_size=self.current_size,
                                  total_length=self.total_length,
                                  displayed_time=displayed_time,
                                  prefix=self.prefix)
                continue

            current_size, total_length = task
            displayed_time = time.time() - self.initial_time
            self.print_status(current_size=current_size,
                              total_length=total_length,
                              displayed_time=displayed_time,
                              prefix=self.prefix)
            self.display_queue.task_done()
            if current_size == total_length:
                # once we have done uploading everything return
                self.done_progress()
                return

    def update(self, size):
        """
        Update object size to be showed. This method called while uploading
        :param size: Object size to be showed. The object size should be in
                     bytes.
        """
        if not isinstance(size, int):
            raise ValueError('{} type can not be displayed. '
                             'Please change it to Int.'.format(type(size)))

        self.current_size += size
        self.display_queue.put((self.current_size, self.total_length))

    def done_progress(self):
        self.total_length = 0
        self.object_name = None
        self.last_printed_len = 0
        self.current_size = 0

    def print_status(self, current_size, total_length, displayed_time, prefix):
        formatted_str = prefix + format_string(
            current_size, total_length, displayed_time)
        self.stdout.write(_REFRESH_CHAR + formatted_str + ' ' *
                          max(self.last_printed_len - len(formatted_str), 0))
        self.stdout.flush()
        self.last_printed_len = len(formatted_str)


def seconds_to_time(seconds):
    """
    Consistent time format to be displayed on the elapsed time in screen.
    :param seconds: seconds
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, m = divmod(minutes, 60)
    if hours:
        return _HOURS_OF_ELAPSED % (hours, m, seconds)
    else:
        return _MINUTES_OF_ELAPSED % (m, seconds)


def format_string(current_size, total_length, elapsed_time):
    """
    Consistent format to be displayed on the screen.
    :param current_size: Number of finished object size
    :param total_length: Total object size
    :param elapsed_time: number of seconds passed since start
    """

    n_to_mb = current_size / _KILOBYTE / _KILOBYTE
    elapsed_str = seconds_to_time(elapsed_time)

    rate = _RATE_FORMAT % (
            n_to_mb / elapsed_time) if elapsed_time else _UNKNOWN_SIZE
    frac = float(current_size) / total_length
    bar_length = int(frac * _BAR_SIZE)
    bar = (_FINISHED_BAR * bar_length +
           _REMAINING_BAR * (_BAR_SIZE - bar_length))
    percentage = _PERCENTAGE_FORMAT % (frac * 100)
    left_str = (
        seconds_to_time(
            elapsed_time / current_size * (total_length - current_size))
        if current_size else _UNKNOWN_SIZE)

    humanized_total = _HUMANINZED_FORMAT % (
            total_length / _KILOBYTE / _KILOBYTE) + _STR_MEGABYTE
    humanized_n = _HUMANINZED_FORMAT % n_to_mb + _STR_MEGABYTE

    return _DISPLAY_FORMAT % (bar, humanized_n, humanized_total, percentage,
                              elapsed_str, left_str, rate)


def _getallfiles(folder):
    filepath_list = []
    for root, folder_names, file_names in os.walk(folder):
        for file_name in file_names:
            file_path = root + os.sep + file_name
            filepath_list.append(file_path)
            print(file_path)
    file_path = sorted(file_path, key=str.lower)
    return filepath_list
