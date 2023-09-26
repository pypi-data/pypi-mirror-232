import os.path

from sandbox_func.common.log.AwLogger import AwLogger
from sandbox_func.model.SandboxFuncManager import SandboxFuncManager

log = AwLogger.getLogger(__name__)
DEFAULT_PROJ_ROOT_DIR = '/mnt/scf'
# DEFAULT_PROJ_ROOT_DIR = 'E:/source/python/sandbox-root'


class SandboxProjManager:

    def __init__(self, proj_root_dir: str = DEFAULT_PROJ_ROOT_DIR):
        self.proj_root_dir = proj_root_dir

    def walkJson(self):
        root_dir = self.proj_root_dir
        if not os.path.exists(root_dir):
            root_dir = DEFAULT_PROJ_ROOT_DIR

        for proj_name in os.listdir(root_dir):
            proj_dir = os.path.join(root_dir, proj_name)
            if os.path.isdir(proj_dir):
                SandboxFuncManager.read_repo_path(proj_dir)
