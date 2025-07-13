from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.action_builder import ActionBuilder
import time

def scrape_instagram_followers_following(username, password):

    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/92.0.4515.159 Safari/537.36")


    driver = webdriver.Chrome()
    driver.get('https://www.instagram.com/accounts/login/')

    # Login
    username_field = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//*[@name='username' or @name='email']"))
    )

    password_field = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//*[@name='password' or @name='pass']"))
    )

    username_field.send_keys(username)
    password_field.send_keys(password)
    password_field.submit()

    time.sleep(7)

    # Look for either verification text or label to appear.
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Check your email') or (self::label and contains(text(), 'Code'))]")
            )
        )
        print("Verification prompt detected. Waiting for user to complete verification...")
        while True:
            try:
                driver.find_element(
                    By.XPATH,
                    "//*[contains(text(), 'Check your email') or (self::label and contains(text(), 'Code'))]"
                )
                print("Still waiting for user verification...")
                time.sleep(3)
            except Exception:
                print("Verification completed, continuing...")
                break
    except Exception:
        pass


    followers = set(get_connections(driver, 'followers', username))

    time.sleep(2)
    following = set(get_connections(driver, 'following', username))

    driver.quit()

    return {
        "followers": list(followers),
        "following": list(following)
    }

def get_connections(driver, connection_type, username):

    driver.get(f'https://www.instagram.com/{username}/')
    time.sleep(3)
    driver.get(f'https://www.instagram.com/{username}/')
    time.sleep(3)

    span_elements = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.XPATH, "//span[contains(@class, 'html-span')]"))
    )

    if connection_type == "followers":
        total_users = int(span_elements[2].text)
    else:
        total_users = int(span_elements[3].text)

    print ("total " + connection_type + ": " + str(total_users))

    try:
        # Click the appropriate button
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
            (By.XPATH, f"//a[contains(@href, '/{connection_type}/')]"))
        ).click()
        time.sleep(2)

        # Scroll parameters
        scroll_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@role='dialog']//div[contains(@class, 'x1n2onr6')]")
            )
        )
        time.sleep(2)

        # Calculate the center of the scroll_box in viewport coordinates
        box_location = scroll_box.location
        box_size = scroll_box.size
        center_x = box_location["x"] + box_size["width"] / 2
        center_y = box_location["y"] + box_size["height"] / 2

        mouse = PointerInput("mouse", "default")
        actions = ActionBuilder(driver, mouse)

        count = 0
        users = []

        while len(users) != total_users:

            prev_users = len(users)

            # Build the action chain:
            actions.pointer_action.move_to_location(center_x, center_y)
            actions.pointer_action.pointer_down(button=1)  # Press middle button
            actions.pointer_action.move_to_location(center_x, center_y + 400).pause(3)
            actions.pointer_action.pointer_up(button=1)  # Release the middle button
            actions.perform()

            users = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[@role='dialog']//span[contains(@class, '_aaco') and @dir='auto']")
                )
            )

            # Failsafe
            if prev_users == len(users): count+=1
            if count == 3: break

        print(connection_type + " found: " + str(len(users)))
        return list({user.text for user in users})

    except Exception as e:
        print(f"Error getting {connection_type}: {str(e)}")
        return []