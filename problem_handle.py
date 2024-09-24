
import os
import subprocess
import hashlib
import stat


def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("FFmpeg is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("FFmpeg is not available")
        return False 
    
def check_tmp_permissions():
    tmp_dir = '/tmp'
    tmp_perms = oct(os.stat(tmp_dir).st_mode)[-3:]
    print(f"Permissions for {tmp_dir}: {tmp_perms}")
    
    if tmp_perms != '777':
        return False

    for item in os.listdir(tmp_dir):
        path = os.path.join(tmp_dir, item)
        mode = os.stat(path).st_mode
        perms = oct(mode)[-3:]
        file_type = 'dir' if stat.S_ISDIR(mode) else 'file'
        print(f"{file_type.capitalize()}: {item}, Permissions: {perms}")
        
        if file_type == 'dir' and perms != '777':
            return False
        elif file_type == 'file' and perms != '666':
            return False

    return True
        
        
def verify_file_integrity(original_path, copied_path):
    def get_file_info(path):
        size = os.path.getsize(path)
        with open(path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return size, file_hash

    original_size, original_hash = get_file_info(original_path)
    copied_size, copied_hash = get_file_info(copied_path)

    print(f"Original file: size={original_size}, hash={original_hash}")
    print(f"Copied file: size={copied_size}, hash={copied_hash}")

    if original_size == copied_size and original_hash == copied_hash:
        print("File integrity verified: The copied file is identical to the original.")
        return True
    else:
        print("File integrity check failed: The copied file differs from the original.")
        return False