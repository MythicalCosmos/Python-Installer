import subprocess
import sys
import os
import time
import urllib.request
import shutil

# Check if another instance of the script is running by looking for a lock file
def is_another_instance_running():
    return os.path.exists("package_installer.lock")

# Create a lock file to indicate that the script is running
def create_lock_file():
    with open("package_installer.lock", "w") as f:
        f.write("")

# Remove the lock file to indicate the script has finished running
def remove_lock_file():
    if os.path.exists("package_installer.lock"):
        os.remove("package_installer.lock")

# Install a list of Python packages using pip
# This function ensures required Python packages are installed, using pip.
def install_packages(packages):
    for package in packages:
        try:
            # Check if the package is already installed
            subprocess.check_output([sys.executable, "-m", "pip", "show", package])
            print(f"{package} is already installed.")
        except subprocess.CalledProcessError:
            # Install the package if it is not installed
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} installed.")

# Download and extract a Python tarball from a given URL
# This function downloads and extracts a specific Python version tarball from the provided URL.
def download_and_extract_python(url):
    try:
        urllib.request.urlretrieve(url, "Python.tgz")
        print("Python tarball downloaded successfully.")
        shutil.unpack_archive("Python.tgz", "PythonExtracted")
        print("Python tarball extracted successfully.")
    except Exception as e:
        print("Error downloading or extracting Python tarball:", e)

# Download the get-pip.py script if pip is not installed
def download_get_pip():
    try:
        # Check if pip is already installed
        subprocess.check_output([sys.executable, "-m", "pip", "--version"])
        print("Pip is already installed.")
    except subprocess.CalledProcessError:
        try:
            # Download get-pip.py if pip is missing
            urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "get-pip.py")
            print("get-pip.py downloaded successfully.")
        except Exception as e:
            print("Error downloading get-pip.py:", e)

# Install pip using the downloaded get-pip.py script
def install_pip():
    try:
        # Check if pip is already installed
        subprocess.check_output([sys.executable, "-m", "pip", "--version"])
        print("Pip is already installed.")
    except subprocess.CalledProcessError:
        try:
            # Run get-pip.py to install pip
            subprocess.check_call([sys.executable, "get-pip.py"])
            print("Pip installed successfully.")
            time.sleep(5)
            # Delete the get-pip.py script after installation
            delete_file("get-pip.py")
        except Exception as e:
            print("Error installing pip:", e)

# Check if Python is installed, and download the most recent version if not
def install_python():
    try:
        # Check if Python is already installed
        subprocess.check_output([sys.executable, "--version"])
        print("Python is already installed.")
    except FileNotFoundError:
        try:
            # Fetch the latest Python version URL dynamically
            latest_version_url = "https://www.python.org/ftp/python/" + urllib.request.urlopen("https://www.python.org/ftp/python/").read().decode().split('"')[1] + "Python.tgz"
            print("Downloading the latest Python version.")
            download_and_extract_python(latest_version_url)
            time.sleep(5)
            # Delete the downloaded tarball after extraction
            delete_file("Python.tgz")
        except Exception as e:
            print("Error determining or downloading the latest Python version:", e)

# Delete a file if it exists
def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    else:
        print(f"File '{file_path}' does not exist.")

# Main function to coordinate the installation process
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

# Entry point of the script
if __name__ == "__main__":
    main()
