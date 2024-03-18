## Installation (Debian)

1. **Install dependencides:**
    ```bash
    sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0
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

5. **Run the flask WebServer:**
    ```bash
    python -m flask --app WebServer run
    ```

6. **Run the MediaPlayer:**
    ```bash
    python MediaPlayer.py [path/to/html]
    ```
