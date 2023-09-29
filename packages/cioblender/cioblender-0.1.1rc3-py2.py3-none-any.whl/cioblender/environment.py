
from cioblender import software, util
def resolve_payload(**kwargs):
    """Resolve the payload for the environment."""

    # Get unique paths from packages with non-empty 'path' attribute
    paths = list({package.get("path") for package in software.packages_in_use(**kwargs) if package.get("path")})

    # Join the unique paths with ":"
    blender_path = ":".join(paths)
    # blender_path = util.clean_path(blender_path)

    # Todo: do we need to add the other paths?
    # blender_path = ":".join([blender_path, "/usr/local/sbin", "/usr/local/bin", "/usr/sbin", "/usr/bin", "/sbin", "/bin"])

    # Define a dictionary for environment variables
    env_dict = {
        "PATH": blender_path,
        #"ADSKFLEX_LICENSE_FILE": "@conductor-adlm",
        "CONDUCTOR_PATHHELPER": "0",
        "HDF5_USE_FILE_LOCKING": "FALSE",
        # "LC_ALL": "C",
        #"LD_LIBRARY_PATH": "/usr/local/nvidia/lib64",
        "__conductor_letter_drives__": "1"
    }


    return {"environment": env_dict}