import platform
import subprocess
import os
import tempfile


def is_homebrew_installed():
    try:
        subprocess.run(
            ["brew", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_ffmpeg_installed():
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_architecture():
    return platform.machine()


def install_homebrew():
    arch = get_architecture()
    if arch == "arm64":
        command = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    elif arch == "x86_64":
        command = 'arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    else:
        print("Unsupported architecture")
        return False

    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def uninstall_homebrew():
    try:
        command = 'yes | /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh)"'
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def install_ffmpeg():
    try:
        subprocess.run("brew install ffmpeg", shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def uninstall_ffmpeg():
    if not is_ffmpeg_installed():
        return True
    try:
        subprocess.run(["brew", "uninstall", "ffmpeg"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def run_command_with_sudo(command):
    try:
        # Create temporary file to store command
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(command)
            temp_file_path = temp_file.name

        # Use temporary file in osascript command
        osascript_command = f"""
        osascript -e 'do shell script "sh {temp_file_path}" with administrator privileges'
        """
        subprocess.run(osascript_command, shell=True, check=True)

        # Delete temporary file after use
        os.unlink(temp_file_path)
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        # Make sure the temporary file is deleted in any case
        if "temp_file_path" in locals():
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass


def install_homebrew_with_password():
    arch = get_architecture()
    if arch == "arm64":
        install_script = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    elif arch == "x86_64":
        install_script = 'arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    else:
        print("Unsupported architecture")
        return False

    try:
        # Create temporary file to store installation script
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".sh"
        ) as temp_file:
            temp_file.write(install_script)
            temp_file_path = temp_file.name

        # Make temporary file executable
        os.chmod(temp_file_path, 0o755)

        # AppleScript to run installation with administrator privileges
        applescript = f"""
        do shell script "{temp_file_path}" with administrator privileges
        """

        # Run AppleScript
        process = subprocess.Popen(
            ["osascript", "-e", applescript],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Error: {stderr.decode('utf-8')}")
            return False

        return True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False
    finally:
        # Make sure the temporary file is deleted in any case
        if "temp_file_path" in locals():
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
