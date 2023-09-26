import configparser
import platform
import os

if platform.system().lower() == 'windows':
    path = r'd:/smartnotebook/snb_node/snb_node/config/config.ini'
    pem_path=r"d:/smartnotebook/snb_node/snb_node/config/private.pem"
else:
    path = r'/home/.config/config.ini'
    pem_path=r'/home/.config/private.pem'

config = configparser.ConfigParser()
config.read(path)

#"http://172.30.81.116:8888"
SNB_SERVER_URL = config.get('snb_server_url', 'url')

workspace_uid = config.get('workspace', 'workspace_uid')
envir_uid = config.get('workspace', 'envir_uid')

cull_idle_timeout_int = config.getint('kernel', 'cull_idle_timeout')


with open(pem_path, "r", encoding='UTF-8') as f:
    pem = f.read()


BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))