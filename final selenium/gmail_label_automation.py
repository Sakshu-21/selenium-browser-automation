"""
Gmail Selenium Automation - Search Spam by Sender + Apply Label
------------------------------------------------------------
Uses your existing Default Chrome profile (already logged into Gmail).
No login, no password, nothing typed anywhere in this script.

BEFORE RUNNING EACH TIME:
- Close ALL Chrome windows completely.
- Check Task Manager (Ctrl+Shift+Esc) for any lingering "Google Chrome"
  background processes and end them too - this profile can only be
  used by one Chrome process at a time.

Requirements:
    pip install selenium
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import traceback

# ============================================================
USER_DATA_DIR = r"C:\Users\saksh\AppData\Local\Google\Chrome\User Data"
PROFILE_DIRECTORY = "Default"
# ============================================================


def create_driver():
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={USER_DATA_DIR}")
    chrome_options.add_argument(f"profile-directory={PROFILE_DIRECTORY}")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def open_gmail(driver, wait):
    print("Step 1: Opening Gmail...")
    driver.get("https://mail.google.com")
    wait.until(EC.presence_of_element_located((By.NAME, "q")))
    print("   -> Inbox loaded.")


def open_spam_folder(driver, wait):
    print("Step 2: Opening Spam folder...")
    try:
        spam_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '#spam')]"))
        )
        spam_link.click()
    except TimeoutException:
        try:
            more_link = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='More']"))
            )
            more_link.click()
            spam_link = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '#spam')]"))
            )
            spam_link.click()
        except TimeoutException:
            print("   -> Couldn't find the Spam link in the sidebar, going by direct URL instead.")
            driver.get("https://mail.google.com/mail/u/0/#spam")

    time.sleep(2)
    print("   -> Spam folder loaded.")


def search_by_sender(driver, wait, sender):
    print(f"Step 3: Searching Spam for emails from '{sender}'...")
    search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
    search_box.clear()
    search_box.send_keys(f"in:spam from:{sender}")
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)
    print("   -> Search complete.")


def get_email_rows(driver):
    return driver.find_elements(By.CSS_SELECTOR, "tr.zA")


def label_email(driver, wait, row, label_name):
    ActionChains(driver).move_to_element(row).perform()

    more_button = row.find_element(By.CSS_SELECTOR, "div[aria-label='More']")
    more_button.click()

    label_as_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Label as']"))
    )
    label_as_option.click()

    label_checkbox = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//div[@role='menuitemcheckbox'][.//span[text()='{label_name}']]")
        )
    )
    label_checkbox.click()

    apply_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[text()='Apply']"))
    )
    apply_button.click()
    time.sleep(1)


def main():
    sender_name = input("Enter the sender's full email (preferred) or name to search for in Spam: ").strip()
    if not sender_name:
        print("Sender cannot be empty. Exiting.")
        return

    driver = create_driver()
    wait = WebDriverWait(driver, 15)

    try:
        open_gmail(driver, wait)
        open_spam_folder(driver, wait)
        search_by_sender(driver, wait, sender_name)

        rows = get_email_rows(driver)
        print(f"Found {len(rows)} email(s) from '{sender_name}' in Spam.")

        if not rows:
            print("No matching emails found. Nothing to label. Exiting.")
            return

        label_name = input("Enter the exact label name (as it appears in Gmail) to apply: ").strip()
        if not label_name:
            print("Label name cannot be empty. Exiting.")
            return

        print(f"Step 4: Applying label '{label_name}' to {len(rows)} email(s)...")
        success_count = 0
        for i, row in enumerate(rows, start=1):
            try:
                label_email(driver, wait, row, label_name)
                success_count += 1
                print(f"   -> Labeled email {i}/{len(rows)}")
            except (TimeoutException, NoSuchElementException) as e:
                print(f"   -> Skipped email {i}/{len(rows)} due to: {e}")
                continue

        print(f"Done. Successfully labeled {success_count} out of {len(rows)} emails.")

    except Exception:
        print("\nSomething went wrong. Full error below:\n")
        traceback.print_exc()
    finally:
        input("\nPress Enter to close this script (Chrome will stay open)...")


if __name__ == "__main__":
    main()