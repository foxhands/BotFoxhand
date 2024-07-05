# Discord Bot with FTP Image Upload

This Discord bot is designed to handle messages containing links and images, upload images to an FTP server, and post URLs to Discord threads accordingly.

## Features

- **Link Handling:** Detects and processes messages containing YouTube and TikTok links.
- **Image Handling:** Detects and processes messages with image attachments.
- **FTP Upload:** Uploads images to an FTP server and generates URLs for sharing.
- **Discord Threads:** Posts URLs to designated Discord threads ('Видосики' and 'Картинки').

## Requirements

- Python 3.6+
- Discord.py library
- ftplib (Python Standard Library)

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/your-repository.git
   cd your-repository


## Install dependencies:

    pip install -r requirements.txt

## Configuration:

    Set up environment variables for FTP credentials and Discord bot token.
    Create a .env file with the following variables:

    ```
    FTP_HOST=your_ftp_host
    FTP_USER=your_ftp_username
    FTP_PASS=your_ftp_password
    FTP_PATH=your_ftp_directory_path
    DOMAIN=your_domain_name
    TOKEN=your_discord_bot_token
    ```

## Run the bot:

    ```
    python main.py
    ```

## Usage:

    Links: When the bot detects supported link types, it posts them to the 'Видосики' thread.
    Images: When the bot detects image attachments, it uploads them to the FTP server and posts the URL to the 'Картинки' thread.

## Contributing:

    Contributions are welcome! Feel free to open issues and pull requests.

## License:

    The source code for the site is licensed under the MIT license, which you can find in the MIT-LICENSE.txt file.
