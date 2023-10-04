from selenium import webdriver
import chromedriver_binary  # Adds chromedriver binary to path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pygetwindow as gw
import webbrowser
import time

BROWSER_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
DRIVER_DIR = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\117.1.58.135"


def check_and_open_webpage_sel(url: str, driver_path: str = DRIVER_DIR):
    # Initialize the web driver
    options = webdriver.ChromeOptions()
    options.binary_location = BROWSER_EXE  # Update this path to your Brave browser executable
    driver = webdriver.Chrome(options=options)

    # Fetch existing window handles (i.e., tabs)
    initial_window_handles = driver.window_handles

    # Loop through each tab
    for handle in initial_window_handles:
        driver.switch_to.window(handle)
        time.sleep(1)  # Pause to allow the tab to load

        if driver.current_url == url:
            print(f"Found URL {url} in existing tab.")
            return  # Return if URL is found

    # If this point is reached, the URL was not found in any tab.
    # Open a new tab and navigate to the URL
    driver.execute_script(f"window.open('{url}');")

    print(f"Opened {url} in a new tab.")


def check_and_open_webpage(url: str, title_keyword=None, browser: str = "brave"):
    webbrowser.register(browser, None, webbrowser.BackgroundBrowser(BROWSER_EXE))

    # Check if any window has a title containing the specified keyword
    matching_windows = None
    if title_keyword:
        matching_windows = [window for window in gw.getAllTitles() if title_keyword in window]

    if matching_windows:
        # Activate the first matching window
        window = gw.getWindowsWithTitle(matching_windows[0])[0]
        window.activate()
    else:
        # Open a new tab with the URL
        webbrowser.get(browser).open_new_tab(url)

    time.sleep(2)  # Allow some time for the action to complete


if __name__ == '__main__':
    url = "http://localhost:5000"
    check_and_open_webpage(url, "FEA - Mesh viewer")
