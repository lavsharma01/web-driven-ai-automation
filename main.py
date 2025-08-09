import sys
import csv
from playwright.sync_api import sync_playwright

# ✅ SCRAPE USERS from Notion
def scrape_users(page):
    # Scroll down to load all visible users
    page.mouse.wheel(0, 10000)
    page.wait_for_timeout(2000)

    # Get all <div> elements that have a 'title' attribute (names/emails)
    all_titles = page.locator("div[title]")
    users = []
    i = 0

    # Walk through the titles two at a time → name then email
    while i < all_titles.count() - 1:
        t1 = all_titles.nth(i).get_attribute("title")
        t2 = all_titles.nth(i + 1).get_attribute("title")

        if t1 and t2 and "@" in t2 and " " in t1:
            users.append([t1, t2])
            i += 2
        else:
            i += 1

    # Write the extracted users to a CSV file
    with open("users.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Email"])
        writer.writerows(users)

    print("✅ Saved to users.csv")

# ✅ ADD USER by sending an invite email
def invite_user(page):
    new_email = input("📧 Enter email to invite: ")

    print("🔘 Clicking 'Add members' button...")
    page.wait_for_timeout(1000)
    page.click("div[role='button']:has-text('Add members')")
    page.wait_for_timeout(1000)

    print("✍️ Typing email...")
    page.fill("input[type='email']", new_email)
    page.wait_for_timeout(1500)  # wait for Notion to show dropdown

    print("🔽 Selecting suggested email from dropdown...")
    page.keyboard.press("ArrowDown")   # move to the suggestion
    page.keyboard.press("Enter")       # select the suggestion
    page.wait_for_timeout(1000)

    print("📨 Clicking 'Send invite'...")
    send_btn = page.locator("div[role='button']:has-text('Send invite')")
    send_btn.wait_for(state="visible", timeout=5000)
    send_btn.click()
    page.wait_for_timeout(1000)

    print(f"✅ Invite sent to {new_email}!")


# ✅ REMOVE USER from workspace
from playwright.sync_api import sync_playwright

def remove_member(email_to_remove):
    with sync_playwright() as p:
        print("🚀 Launching with saved session (no login needed)...")
        context = p.chromium.launch_persistent_context(
            user_data_dir="auth_storage",  # Folder where session is stored
            headless=False,
            slow_mo=100
        )
        page = context.new_page()

        print("📍 Navigating to Members tab...")
        page.goto("https://www.notion.so/settings/members", timeout=90000)

        try:
            print("⌛ Waiting for member table to load...")
            page.wait_for_selector('[data-testid="workspace-members-table"]', timeout=15000)
        except:
            print("❌ Member table did not load.")
            context.close()
            return

        print(f"🔍 Searching for user: {email_to_remove}")
        row_selector = f'tr:has-text("{email_to_remove}")'
        try:
            row = page.locator(row_selector)
            row.wait_for(timeout=5000)
        except:
            print(f"❌ User row for {email_to_remove} not found.")
            context.close()
            return

        print("🔽 Clicking Role dropdown...")
        try:
            dropdown = row.locator('[data-testid="role-select-dropdown-button"]')
            dropdown.click()
            page.wait_for_timeout(1000)  # Wait for dropdown animation
        except:
            print("❌ Failed to click Role dropdown.")
            page.screenshot(path="error_dropdown.png")
            context.close()
            return

        print("🗑️ Clicking 'Remove from workspace' option...")
        try:
            remove_option = page.get_by_text("Remove from workspace", exact=True)
            remove_option.wait_for(timeout=5000)
            remove_option.click()
        except:
            print("❌ 'Remove from workspace' not found.")
            page.screenshot(path="error_remove_option.png")
            context.close()
            return

        print("⚠️ Waiting for confirmation modal...")
        try:
            page.wait_for_selector('[data-testid="confirmation-modal"]', timeout=5000)
            confirm_button = page.locator('button:has-text("Remove ")')
            confirm_button.wait_for(timeout=3000)
            confirm_button.click()
        except:
            print("❌ Confirmation modal/button not found.")
            page.screenshot(path="error_confirm.png")
            context.close()
            return

        print(f"✅ Successfully removed: {email_to_remove}")
        page.pause()
        context.close()


# ✅ MAIN flow that runs based on what you ask
def run(action):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show the browser window
        context = browser.new_context()
        page = context.new_page()

        # Step 1: Open Notion login page
        page.goto("https://www.notion.so/login", timeout=60000)

        # Step 2: Let user login manually (handle 2FA)
        input("🔐 Login manually, then press Enter...")

        # Step 3: Let user go to Members or Guests page
        input("📍 Go to Members or Guests tab, then press Enter...")

        # Step 4: Run the selected action
        if action == "scrape":
            scrape_users(page)
        elif action == "add":
            invite_user(page)
        elif action == "remove":
            remove_user(page)
        else:
            print("❌ Unknown action. Use: scrape, add, or remove")

        input("🔚 Press Enter to close browser...")
        browser.close()

# ✅ Entry point when you run the script from terminal
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("⚠️  Usage: python main.py [scrape|add|remove]")
    else:
        run(sys.argv[1])

from playwright.sync_api import sync_playwright

def save_login_session():
    with sync_playwright() as p:
        print("🧠 Launching browser to save login session...")
        context = p.chromium.launch_persistent_context(
            user_data_dir="auth_storage",  # This folder stores your logged-in state
            headless=False
        )
        page = context.new_page()
        page.goto("https://www.notion.so/login", timeout=90000)

        print("🔐 Login manually (enter Gmail & OTP in browser)...")
        input("👉 Once you're logged into Notion, press Enter here to save session...")

        print("✅ Session saved. You won’t need to login again.")
        context.close()

