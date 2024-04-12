import subprocess
import sys
import os
import time
import urllib.request
import shutil

def is_another_instance_running():
    return os.path.exists("package_installer.lock")

def create_lock_file():
    with open("package_installer.lock", "w") as f:
        f.write("")

def remove_lock_file():
    if os.path.exists("package_installer.lock"):
        os.remove("package_installer.lock")

def install_packages(packages):
    for package in packages:
        try:
            subprocess.check_output([sys.executable, "-m", "pip", "show", package])
            print(f"{package} is already installed.")
        except subprocess.CalledProcessError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} installed.")

def download_and_extract_python(url):
    try:
        urllib.request.urlretrieve(url, "Python.tgz")
        print("Python tarball downloaded successfully.")
        shutil.unpack_archive("Python.tgz", "PythonExtracted")
        print("Python tarball extracted successfully.")
    except Exception as e:
        print("Error downloading or extracting Python tarball:", e)

def download_get_pip():
    try:
        subprocess.check_output([sys.executable, "-m", "pip", "--version"])
        print("Pip is already installed.")
    except subprocess.CalledProcessError:
        try:
            urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "get-pip.py")
            print("get-pip.py downloaded successfully.")
        except Exception as e:
            print("Error downloading get-pip.py:", e)

def install_pip():
    try:
        subprocess.check_output([sys.executable, "-m", "pip", "--version"])
        print("Pip is already installed.")
    except subprocess.CalledProcessError:
        try:
            subprocess.check_call([sys.executable, "get-pip.py"])
            print("Pip installed successfully.")
            time.sleep(5)
            delete_file("get-pip.py")
        except Exception as e:
            print("Error installing pip:", e)

def install_python():
    try:
        subprocess.check_output([sys.executable, "--version"])
        print("Python is already installed.")
    except FileNotFoundError:
        python_url = "https://www.python.org/ftp/python/3.12.2/Python-3.12.2.tgz"
        download_and_extract_python(python_url)
        time.sleep(5)
        delete_file("Python.tgz")

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    else:
        print(f"File '{file_path}' does not exist.")

def main():
    if is_another_instance_running():
        print("Another instance of the package installer script is already running.")
        return
    create_lock_file()
    install_python()
    download_get_pip()
    install_pip()
    packages_to_install = ["placeholder have whatever packages you want to install."]
    install_packages(packages_to_install)
    remove_lock_file()
    time.sleep(2)

if __name__ == "__main__":
    main()
