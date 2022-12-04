import os


def list_assets(root, dir_build):
    """Gathers the list of all assets.

    Args:
        root(str): Path to base-directory in which projects are stored.
        dir_build(str): Base path of the build_dir

    Returns:
        assets(list of str): List of asset names that are part of this project
    """
    if root is not None:  # check for asset
        # build_path = os.path.join(self.root, self.current_project_name, 'build')
        if os.path.isdir(dir_build) is False:
            return []
        else:
            return os.listdir(dir_build)
    else:
        return []


def get_build_dir(root, project_name):
    """Generates the path to the build directory.

    Args:
        root(str): Path to base-directory in which projects are stored.
        project_name(str): Name of the project.

    Returns:
        dir_build(str): Path to the build directory.
    """
    if '-' in project_name:
        return os.path.join(root, project_name.split('-')[0], 'build')
    else:
        return os.path.join(root, project_name, 'build')

