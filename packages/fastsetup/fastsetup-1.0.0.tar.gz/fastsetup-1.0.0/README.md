# fastsetup

A Python library that has all the static repetitive code used in Python scripts, for easier and faster setup.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install fastsetup.

```bash
pip install fastsetup
```

## Usage and docs

```python
import fastsetup

loggerMain, loggerInit, loggerProcess = fastsetup.main_log(log_folder)
# -----------------------------------------------------------------------
# Function: main_log(log_folder)
# Description: Creates and configures a main log and two additional logs.
# Parameters:
#   - log_folder (str): The folder path where log files will be stored.
# Returns:
#   - loggerMain (Logger): The main logger.
#   - loggerInit (Logger): The initialization logger.
#   - loggerProcess (Logger): The process logger.
# -----------------------------------------------------------------------

customLog = fastsetup.custom_log(log_folder, log_format, log_name)
# -----------------------------------------------------------------------
# Function: custom_log(log_folder, log_format, log_name)
# Description: Creates a custom log with a specified format.
# Parameters:
#   - log_folder (str): The folder path where log files will be stored.
#   - log_format (str): The format for log messages (default format used if None).
#   - log_name (str): The name for the custom log.
# Returns:
#   - customLog (Logger): The custom logger.
# -----------------------------------------------------------------------

Config_Name = fastsetup.get_config(Config_Path, SheetName, Key, Value)
# -----------------------------------------------------------------------
# Function: get_config(Config_Path, SheetName, Key, Value)
# Description: Reads a configuration file (Excel) and returns a dictionary.
# Parameters:
#   - Config_Path (str): The path to the configuration Excel file.
#   - SheetName (str): The name of the sheet within the Excel file.
#   - Key (str): The column name representing keys.
#   - Value (str): The column name representing values.
# Returns:
#   - Config (dict): A dictionary containing key-value pairs from the configuration.
# -----------------------------------------------------------------------

fastsetup.SMTP(config)
# -----------------------------------------------------------------------
# Function: SMTP(config)
# Description: Sends an email with attachments using SMTP protocol.
# Parameters:
#   - config (dict): A dictionary containing email configuration details.
#     Required keys: 'file_name', 'sender_email', 'to_email', 'email_subject',
#     'body_type', 'body', 'cc', 'attachments', 'server', 'port'.
# -----------------------------------------------------------------------

file_Name = fastsetup.SFTP_download(config)
# -----------------------------------------------------------------------
# Function: SFTP_download(config)
# Description: Downloads a file from a remote server using SFTP.
# Parameters:
#   - config (dict): A dictionary containing SFTP configuration details.
#     Required keys: 'host', 'user_name', 'password', 'SFTP_port',
#     'server_folder_name', 'server_file_name', 'local_file_path'.
# Returns:
#   - result: downloaded file.
# -----------------------------------------------------------------------

fastsetup.SFTP_upload(config)
# -----------------------------------------------------------------------
# Function: SFTP_upload(config)
# Description: Uploads a file to a remote server using SFTP.
# Parameters:
#   - config (dict): A dictionary containing SFTP configuration details.
#     Required keys: 'host', 'user_name', 'password', 'SFTP_port',
#     'local_file', 'target_location'.
# -----------------------------------------------------------------------

df = fastsetup.oracle_download(Config)
# -----------------------------------------------------------------------
# Function: oracle_download(Config)
# Description: Downloads data from an Oracle database using a provided query.
# Parameters:
#   - Config (dict): A dictionary containing Oracle database configuration details.
#     Required keys: 'host', 'port', 'data_source', 'user_ID', 'password', 'query'.
# Returns:
#   - df (DataFrame): A Pandas DataFrame containing the queried data.
# -----------------------------------------------------------------------

```