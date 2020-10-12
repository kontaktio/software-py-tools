import json
import logging
import os
import random
import sys

from zipfile import ZipFile

random_mac = lambda: ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])


def __get_unique_ids_from_json(json: dict):
    unique_ids = list()
    for device in json:
        unique_ids.append(device["deviceConfig"]["uniqueId"])
    return unique_ids


def __get_unique_ids_from_json_file(file_path: str):
    with open(file_path) as json_file:
        devices = json.load(json_file)
        return __get_unique_ids_from_json(devices)


def __get_unique_ids_from_zip_file(file_path: str):
    unique_ids = list()
    with ZipFile(file_path, "r") as zip:
        device_configs = [
            j.filename
            for j in zip.filelist
            if j.filename.endswith("devices_config.json")
        ]
        for conf in device_configs:
            conf_json = json.loads(zip.read(conf))
            unique_ids.extend(__get_unique_ids_from_json(conf_json))
    return unique_ids


def get_unique_ids(file_path: str):
    if file_path.endswith(".json"):
        return __get_unique_ids_from_json_file(file_path)
    elif file_path.endswith(".zip"):
        return __get_unique_ids_from_zip_file(file_path)
    else:
        return None


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # You can load uniqueIds either from devices_config.json file inside .zip file....
    # input_file = "data/generate_ofm/devices_config.json"

    # ... or from a zip file
    input_file_name = "data/generate_ofm/order_config_KNKT-DQE.zip"

    unique_ids = get_unique_ids(input_file_name)
    if unique_ids:
        logging.info(f"Going to generate CSV file with {len(unique_ids)} devices")
        output_file_name = f"data/generate_ofm/{os.path.splitext(os.path.basename(input_file_name))[0]}.csv"
        with open(output_file_name, "w") as csv_file:
            csv_file.write("#\n")
            for unique_id in unique_ids:
                csv_file.write(f"{unique_id},{random_mac()}")
                csv_file.write("\n")
        print(f"Generated a file with {len(unique_ids)} devices at {output_file_name}")
    else:
        logging.error(f"No devices loaded")
