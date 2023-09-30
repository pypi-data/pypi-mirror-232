import subprocess
import re


def get_remote_List(config_file_path):
    rclone_command = ["rclone","--config",config_file_path,"listremotes"]
    try:
        result = subprocess.run(rclone_command,capture_output=True,text=True,check=True)
        # Extract remote names from the output and remove trailing colons
        output = result.stdout.strip()
        remote_names = [remote_name.rstrip(':') for remote_name in output.split('\n')]
        return remote_names
    except subprocess.CalledProcessError as e:
        return e.stderr



def upload_local_file(config_file_path,local_file_path,remote_name,file_name):
    rclone_command = ["rclone", "--config", config_file_path, "copy", local_file_path, f"{remote_name}:{file_name}"]
    try:
        result = subprocess.run(rclone_command,capture_output=True,text=True,check=True)
        return True
    except subprocess.CalledProcessError as e:
        return False


def remote_upload(config_file_path,link,remote_name,file_name):
    rclone_command = ["rclone", "--config", config_file_path, "copyurl", link, f"{remote_name}:{file_name}"]
    try:
        process = subprocess.run(rclone_command,capture_output=True,text=True,check=True)
        return "true"
    except subprocess.CalledProcessError as e:
        return False


def storage_detail(config_file_path:str,remote_name):
    rclone_command = f"rclone about {remote_name}: --config {config_file_path}"
    try:
        completed_process = subprocess.run(rclone_command,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if completed_process.returncode == 0:
            return completed_process.stdout
        else:
            return completed_process.stderr
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return str(e)




