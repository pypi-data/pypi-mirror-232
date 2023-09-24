import os
import subprocess
import argparse
import shutil
import re
from pathlib import Path
from k_protocol.k_protocol import get_proto_file
# Get the absolute path of the workspace root
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Set the current working directory to the workspace root
os.chdir(workspace_root)
print(f"Current working directory: {workspace_root}")

from create_public_proto import create_public_proto

import subprocess



def remove_unsafe_func()-> str:
    with open("src/k_lights_interface/k_device.py", "r") as f:
        original_code = f.read()
    pattern = r"def\s+set_rgbacl_emitter_channels_without_compensation_unsafe\(.*?\):[\s\S]*?(?=\n\s*def|\Z)"
    safe_code =  re.sub(pattern, "", original_code, flags=re.DOTALL)
    with open("src/k_lights_interface/k_device.py", "w") as f:
        f.write(safe_code)
    return original_code


def main(args: argparse.Namespace)-> int:
    try:
        script_dir = Path(__file__).resolve().parent
        dist_dir = Path(script_dir / ".."/ "dist").resolve()
        shutil.rmtree(dist_dir, ignore_errors=True)
        
        original_k_device_code_str = remove_unsafe_func()

        python_path = args.python_path
        get_proto_file("raw_proto/k_full.proto","master")
        # Create the public proto file
        create_public_proto()
        # Build the public proto file
        ret = subprocess.run([f"{python_path}", '-m', 'grpc_tools.protoc', '-I', 'raw_proto/', '--python_betterproto_out=src/k_lights_interface/', 'k_public.proto'], stdout=subprocess.PIPE, stderr=subprocess.PIPE , text=True)
        if ret.stderr and "No module" in ret.stderr:
            print(f"Unable to generate proto {ret.stderr}")
            return -1
        ret = subprocess.run([f"{python_path}", '-m', 'build'], stdout=subprocess.PIPE, stderr=subprocess.PIPE , text=True)
        if ret.stderr and "No module" in ret.stderr:
            print(f"Unable to build distribution {ret.stderr}")
            return -1
        
        print("Now you can publish the package to pypi using the upload command found in PRIVATE_README.md")
        return 0
    except Exception as e:
        pass
    finally:
        with open("src/k_lights_interface/k_device.py", "w") as f:
            f.write(original_k_device_code_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--python-path",
        action="store_true",
        help="path to the python executable that has the required packages installed",
        default=".venv/Scripts/python.exe",
    )
    args = parser.parse_args()
    ret = main(args)
    if ret != 0:
        print("Failed to publish package")