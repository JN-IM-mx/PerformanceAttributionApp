import paramiko
import os

# Server details
hostname = "dell693srv"
port = 22
username = "autoengine"
password = "autoengine"

# Remote paths and commands
remote_app_directory = "/dell693srv2/apps/qa14640_TPK0002892_75729280"
# remote_csv_files = ["portfolios.csv", "benchmarks.csv"]
local_project_directory = os.path.dirname(os.path.abspath(__file__))

# Commands to execute
commands = [
    # "./PerfContribution.sh --action export",
    'pwd',
    'sqsh -SDELL693SRV -UINSTAL -PINSTALL -DTPK0002892_75729280 -C "SELECT * FROM CONTRIB_PORTFOLIO_PERFORMANCE" -m csv > output.csv'
]


def execute_commands(ssh, commands, remote_directory):
    """
    Execute a list of commands in the specified remote directory.
    """
    try:
        print(f"Changing to remote directory: {remote_directory}")
        commands.insert(0, f"cd {remote_directory}")  # Change directory command
        full_command = " && ".join(commands)  # Combine commands
        stdin, stdout, stderr = ssh.exec_command(full_command)

        # Print command output
        print("Output:")
        print(stdout.read().decode())

        # Print errors, if any
        error_output = stderr.read().decode()
        if error_output:
            print("Errors:")
            print(error_output)

    except Exception as e:
        print(f"Error while executing commands: {e}")


def transfer_files(sftp, remote_files, local_directory):
    """
    Transfer files from the remote server to the local directory.
    """
    try:
        for file_name in remote_files:
            remote_path = remote_app_directory + "/" + file_name
            print(remote_path)
            local_path = os.path.join(local_directory, file_name)
            print(local_path)

            print(f"Transferring {remote_path} to {local_path}...")
            sftp.get(remote_path, local_path)
            print(f"File {file_name} transferred successfully!")
    except Exception as e:
        print(f"Error while transferring files: {e}")


def main():
    try:
        # Initialize SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print("Connecting to the remote server...")
        ssh.connect(hostname, port, username, password)
        print("Connected to the server!")

        # Execute the list of commands
        execute_commands(ssh, commands, remote_app_directory)

        # # Initialize SFTP client
        # sftp = ssh.open_sftp()
        #
        # # Transfer CSV files to the local project directory
        # transfer_files(sftp, remote_csv_files, local_project_directory)
        #
        # # Close SFTP and SSH connections
        # sftp.close()
        ssh.close()
        print("All tasks completed successfully!")

    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
