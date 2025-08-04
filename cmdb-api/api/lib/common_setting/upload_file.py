import base64
import uuid
import os
from io import BytesIO

from flask import abort, current_app
import lz4.frame

from api.lib.common_setting.utils import get_cur_time_str
from api.models.common_setting import CommonFile
from api.lib.common_setting.resp_format import ErrFormat


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_new_file_name(name):
    ext = name.split('.')[-1]
    prev_name = ''.join(name.split(f".{ext}")[:-1])
    uid = str(uuid.uuid4())
    cur_str = get_cur_time_str('_')

    return f"{prev_name}_{cur_str}_{uid}.{ext}"


class CommonFileCRUD:
    @staticmethod
    def add_file(**kwargs):
        return CommonFile.create(**kwargs)

    @staticmethod
    def get_file(file_name, to_str=False):
        existed = CommonFile.get_by(file_name=file_name, first=True, to_dict=False)
        if not existed:
            abort(400, ErrFormat.file_not_found)

        uncompressed_data = lz4.frame.decompress(existed.binary)

        return base64.b64encode(uncompressed_data).decode('utf-8') if to_str else BytesIO(uncompressed_data)

    @staticmethod
    def sync_file_to_db():
        for p in ['UPLOAD_DIRECTORY_FULL']:
            upload_path = current_app.config.get(p, None)
            if not upload_path:
                continue
            for root, dirs, files in os.walk(upload_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if not os.path.isfile(file_path):
                        continue

                    existed = CommonFile.get_by(file_name=file, first=True, to_dict=False)
                    if existed:
                        continue
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    compressed_data = lz4.frame.compress(data)
                    try:
                        CommonFileCRUD.add_file(
                            origin_name=file,
                            file_name=file,
                            binary=compressed_data
                        )

                        current_app.logger.info(f'sync file {file} to db')
                    except Exception as e:
                        current_app.logger.error(f'sync file {file} to db error: {e}')

    def get_file_binary_str(self, file_name):
        return self.get_file(file_name, True)

    def save_str_to_file(self, file_name, str_data):
        try:
            self.get_file(file_name)
            current_app.logger.info(f'file {file_name} already exists')
            return
        except Exception as e:
            # file not found
            pass

        bytes_data = base64.b64decode(str_data)
        compressed_data = lz4.frame.compress(bytes_data)

        try:
            self.add_file(
                origin_name=file_name,
                file_name=file_name,
                binary=compressed_data
            )
            current_app.logger.info(f'save_str_to_file {file_name} success')
        except Exception as e:
            current_app.logger.error(f"save_str_to_file error: {e}")
