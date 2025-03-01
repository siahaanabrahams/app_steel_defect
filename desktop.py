"""
Desktop module.
"""

import subprocess

import webview

PORT = 8500


def start_streamlit_app():
    """Run Streamlit in headless mode using subprocess"""
    subprocess.Popen(
        [
            "streamlit",
            "run",
            "main.py",
            "--server.headless=true",
            f"--server.port={PORT}",
        ]
    )


if __name__ == "__main__":
    # Start the Streamlit app
    start_streamlit_app()

    # Create a pywebview window to display the Streamlit app
    webview.create_window("Streamlit App", f"http://127.0.0.1:{PORT}")
    webview.start()
