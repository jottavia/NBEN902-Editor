# NBEN902 Editor

Current Version 1.8

NBEN902 Editor is a tool for editing fixed-width files with specific column formats. It allows for the addition, modification, and deletion of rows. It also supports member modification by selecting data from an Excel spreadsheet.

For more detailed information, see the [About](ABOUT.md) page.

## Features

- Load fixed-width files for editing.
- Save edited data to a fixed-width file.
- Add new rows manually.
- Modify member data by selecting from an Excel spreadsheet.
- Transmit data using 902-sftp.
- Use tooltips to provide additional information for specific columns.

## Requirements

- Python 3.x
- pandas
- openpyxl
- tkinter
- Paramiko
## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/NBEN902_Editor.git

    Install the required Python packages:

    sh

	pip install Python 3.x
	pip install pandas
	pip install openpyxl
	pip install tkinter
    	pip install pandas openpyxl
   	pip install paramiko

Usage

    Run the main script:

    sh

    python main.py

    Use the interface to open, edit, save, and modify member data.

Project Structure

    src/main.py: The main script to run the application.
    src/editable_table.py: Contains the EditableTable class for managing the table of data.
    src/file_operations.py: Functions for parsing and saving fixed-width files.
    src/member_selector.py: A module for selecting members from an Excel spreadsheet.
    src/utils.py: Utility functions, including tooltip functionality.
    src/sftp_transmitter.py: Handles the SFTP transmission with a detailed dialog and progress indicator.
    .gitignore: Git ignore file to exclude unnecessary files from the repository.
    README.md: Project documentation.

Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.
License

This project is licensed under the MIT License.

### Project Structure

NBEN902_Editor/
├── .gitignore
├── README.md
├── src/
│   ├── main.py
│   ├── editable_table.py
│   ├── file_operations.py
│   ├── member_selector.py
│   └── utils.py
|   ├── sftp_transmitter.py
