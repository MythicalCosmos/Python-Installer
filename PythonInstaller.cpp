#include <iostream>
#include <fstream>
#include <filesystem>
#include <cstdlib>
#include <thread>
#include <chrono>
#include <stdexcept>
#include <string>
#include <sstream>
#include <curl/curl.h>

namespace fs = std::filesystem;

// Check if another instance of the script is running by looking for a lock file
bool isAnotherInstanceRunning() {
    return fs::exists("package_installer.lock");
}

// Create a lock file to indicate that the script is running
void createLockFile() {
    std::ofstream lockFile("package_installer.lock");
    lockFile.close();
}

// Remove the lock file to indicate the script has finished running
void removeLockFile() {
    if (fs::exists("package_installer.lock")) {
        fs::remove("package_installer.lock");
    }
}

// Execute a shell command and return its output
std::string executeCommand(const std::string& command) {
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("Failed to execute command: " + command);
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    return result;
}

// Install a list of Python packages using pip
void installPackages(const std::vector<std::string>& packages) {
    for (const auto& package : packages) {
        try {
            executeCommand("python3 -m pip show " + package);
            std::cout << package << " is already installed." << std::endl;
        } catch (...) {
            std::cout << "Installing package: " << package << std::endl;
            executeCommand("python3 -m pip install " + package);
        }
    }
}

// Callback function for writing data with libcurl
size_t writeData(void* ptr, size_t size, size_t nmemb, void* stream) {
    std::ofstream* out = static_cast<std::ofstream*>(stream);
    out->write(static_cast<char*>(ptr), size * nmemb);
    return size * nmemb;
}

// Download a file using libcurl
void downloadFile(const std::string& url, const std::string& outputFile) {
    CURL* curl = curl_easy_init();
    if (!curl) {
        throw std::runtime_error("Failed to initialize libcurl");
    }

    std::ofstream outFile(outputFile, std::ios::binary);
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeData);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &outFile);

    CURLcode res = curl_easy_perform(curl);
    if (res != CURLE_OK) {
        throw std::runtime_error("Failed to download file: " + url);
    }

    curl_easy_cleanup(curl);
    outFile.close();
}

// Extract a tarball using the system tar command
void extractTarball(const std::string& tarball, const std::string& outputDir) {
    std::string command = "tar -xzf " + tarball + " -C " + outputDir;
    int retCode = std::system(command.c_str());
    if (retCode != 0) {
        throw std::runtime_error("Failed to extract tarball: " + tarball);
    }
}

// Download and extract a Python tarball from a given URL
void downloadAndExtractPython(const std::string& url) {
    try {
        downloadFile(url, "Python.tgz");
        std::cout << "Python tarball downloaded successfully." << std::endl;
        extractTarball("Python.tgz", "PythonExtracted");
        std::cout << "Python tarball extracted successfully." << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Error downloading or extracting Python tarball: " << e.what() << std::endl;
    }
}

// Install pip if not already installed
void installPip() {
    try {
        executeCommand("python3 -m pip --version");
        std::cout << "Pip is already installed." << std::endl;
    } catch (...) {
        std::cout << "Downloading get-pip.py..." << std::endl;
        downloadFile("https://bootstrap.pypa.io/get-pip.py", "get-pip.py");
        executeCommand("python3 get-pip.py");
        std::cout << "Pip installed successfully." << std::endl;
        fs::remove("get-pip.py");
    }
}

// Check if Python is installed, and download the most recent version if not
void installPython() {
    try {
        executeCommand("python3 --version");
        std::cout << "Python is already installed." << std::endl;
    } catch (...) {
        std::cout << "Downloading the latest Python version..." << std::endl;
        std::string pythonUrl = "https://www.python.org/ftp/python/3.12.2/Python-3.12.2.tgz"; // Replace with dynamic fetching if needed
        downloadAndExtractPython(pythonUrl);
    }
}

// Main function to coordinate the installation process
int main() {
    if (isAnotherInstanceRunning()) {
        std::cout << "Another instance of the package installer script is already running." << std::endl;
        return 0;
    }

    createLockFile();

    try {
        installPython();
        installPip();
        std::vector<std::string> packagesToInstall = {"placeholder_package"};
        installPackages(packagesToInstall);
    } catch (const std::exception& e) {
        std::cerr << "An error occurred: " << e.what() << std::endl;
    }

    removeLockFile();
    std::this_thread::sleep_for(std::chrono::seconds(2));

    return 0;
}
