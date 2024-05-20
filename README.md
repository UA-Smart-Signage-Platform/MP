## Installation (Debian)

1. **Install dependencies:**
    ```bash
    sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0 python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1
    ```

2. **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    ```

3. **Activate the virtual environment:**
    ```bash
    source venv/bin/activate
    ```

4. **Install the requirements:**
    ```bash
    pip install -r requirements.txt
    ```

5. **Run the MediaPlayer:**
    ```bash
    python media_player.py
    ```


## Troubleshooting

1. Artifacting in what is being displayed

    this seems to be a problem with the compositor and the command `export WEBKIT_DISABLE_COMPOSITING_MODE=1` seems to fix it

2. MediaPlayer window takes too long to open

    this is a problem with GTK applications and can be fixed by uninstalling/stopping the xdg-desktop-portal

3. When inputing the wrong password in the config page a nm-applet pop up appears asking for password

    this is due to the fact that nm-applet asks for a password when an invalid password is given in an nmcli command. to fix this either remove nm-applet or launch it with the --no-agent flag
    