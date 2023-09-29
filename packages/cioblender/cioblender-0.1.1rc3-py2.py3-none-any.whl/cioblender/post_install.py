import os
import sys

def fslash(path):
    return path.replace("\\", "/")

PLATFORM = sys.platform
PWD = os.path.dirname(os.path.abspath(__file__))
CIO_DIR = fslash(os.path.dirname(PWD))

ADDOON_FILE = os.path.join(PWD, "conductor_submitter_plugin.py")

INIT_CONTENT = """
import sys
CIO_DIR = "{}"
sys.path.insert(1, CIO_DIR)
""".format(CIO_DIR)

def main():
    if not PLATFORM.startswith(("win", "linux", "darwin")):
        sys.stderr.write("Unsupported platform: {}".format(PLATFORM))
        sys.exit(1)

    with open(ADDOON_FILE, "r+", encoding="utf-8") as file:
        content = file.read()
        file.seek(0)
        file.write(INIT_CONTENT + "\n")
        file.write(content)

    sys.stdout.write("Wrote Conductor Blender init file: {}\n".format(ADDOON_FILE))
    sys.stdout.write("Completed Blender addon setup!\n")


if __name__ == "__main__":
    main()
