from time import monotonic

from os.path import join, exists
from os import listdir, makedirs
import pickle


def perform(backup_folder_path: str, currency_rate: dict):
    """
    Backups currency rates dict to filesystem folder specified in settings.py
    """
    if not exists(backup_folder_path):
        makedirs(backup_folder_path)
    backup_file = '.'.join([str(monotonic()), 'bkp'])
    backup_file = join(backup_folder_path, backup_file)
    with open(backup_file, "wb") as backup_file:
        pickle.dump(currency_rate, backup_file)


def load(backup_file_path: str) -> dict:
    """
    Loads currency rate dict from data stored in backup_file_path
    :param backup_file_path: path to file restore from
    """
    with open(backup_file_path, 'rb') as backup_file:
        return pickle.load(backup_file)


def find_latest(backup_folder_path: str) -> str:
    """
    Find backup files in path specified path and
    :return: backup_file_path
    """
    # if not exists(app.config['backup_path']):
    #     return ""
    if not exists(backup_folder_path):
        return ""
    backups = listdir(backup_folder_path)
    if not backups:
        return ""
    backups.sort(reverse=True)
    return join(backup_folder_path, backups[0])
