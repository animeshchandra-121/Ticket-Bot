import sys
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import undetected_chromedriver as uc
from datetime import datetime, time as dt_time

# List of user agents to randomize
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
]


# Simulate random human delays
def human_delay(min_time=0.5, max_time=2.0):
    time.sleep(random.uniform(min_time, max_time))


def is_within_time_range(start_time, end_time):
    current_time = datetime.now().time()

    # If the time range does not cross midnight
    if start_time <= end_time:
        return start_time <= current_time <= end_time
    else:
        # If the time range crosses midnight
        return current_time >= start_time or current_time <= end_time


# Simulate typing text character by character
def human_typing(element, text, delay=0.1):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, delay))


# Initialize the undetected driver to bypass detection
def init_driver(executable_path):
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

    driver = uc.Chrome(options=options)
    return driver


# Function to reload the page
def reload(driver, max_retry=100):
    retry = 0
    while retry <= max_retry:
        try:
            print("Attempting to load the page.......")
            driver.refresh()
            WebDriverWait(driver, 20).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            return True  # Return success after reload and page load
        except (TimeoutException, NoSuchElementException) as e:
            retry += 1
    return False


# Open BookMyShow website
def open_bookmyshow(driver):
    driver.get("https://in.bookmyshow.com/")
    WebDriverWait(driver, 20).until(
        lambda driver: driver.execute_script('return document.readyState') == 'complete'
    )
    human_delay()


# Enter city in search bar
def enter_city(driver, city_name):
    input_city_xpath = "//input[@placeholder='Search for your city']"
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, input_city_xpath))
    )
    input_city = driver.find_element(By.XPATH, input_city_xpath)
    human_typing(input_city, city_name)
    human_delay()
    input_city.send_keys(Keys.ENTER)


# Click on event link
def click_event_link(driver, event_link):
    event = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, event_link))
    )
    event.click()


# Click on movie or event
def click_movie_link(driver, event_name):
    try:
        # Initialize ActionChains for moving and clicking
        actions = ActionChains(driver)

        # Try finding the event with scrolling
        while True:
            # Get all the links on the current visible page
            event_links = driver.find_elements(By.PARTIAL_LINK_TEXT, event_name)

            # If we find the event link, click it
            if event_links:
                print(f"Event '{event_name}' found. Scrolling to it and clicking...")

                # Scroll the element into view using scrollIntoView()
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", event_links[0])
                human_delay()

                # Optionally move to the element before clicking
                actions.move_to_element(event_links[0]).perform()
                human_delay()
                event_links[0].click()
                return

    except Exception as e:
        print(f"Error while searching for the event: {e}")


# Book tickets
def book_tickets(driver, number_of_tickets, max_retry=100):
    attempts = 0
    while attempts <= max_retry:
        try:
            # Locate the "Book Tickets" button by its XPATH and wait until it becomes clickable (max 30 seconds)
            book_tickets_xpath = "//*[@id='synopsis-book-button']"
            book_tickets_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, book_tickets_xpath))
            )

            # Create an action chain to perform human-like mouse movement to the "Book Tickets" button
            actions = ActionChains(driver)
            actions.move_to_element(book_tickets_button).perform()

            # Introduce a human-like delay (0 to 1 second)
            human_delay(0, 0.5)

            # Click the "Book Tickets" button
            book_tickets_button.click()

            # Locate the XPATH to increase the number of tickets count
            ticket_id = "//*[@id='super-container']/div[2]/div[4]/div[1]/div[2]/div[1]/div[2]/div"
            book_ticket = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, ticket_id))
            )
            # Move to the ticket option element and click it
            actions.move_to_element(book_ticket).perform()
            book_ticket.click()

            # Locate the ticket confirmation element (identified by SVG) and wait until it becomes clickable
            tckets_id = "//*[@id='super-container']/div[2]/div[4]/div[1]/div[2]/div[1]/div[2]/div/div[3]"
            collect_ticket = WebDriverWait(driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, tckets_id))
            )
            for i in range(1, number_of_tickets):
                collect_ticket.click()
                human_delay(0.5, 1.0)  # Add a slight delay between clicks

            # Locate the "Proceed" button and wait until it becomes clickable
            proceed_id = "//*[@id='super-container']/div[2]/div[4]/div[2]/div/div[2]"
            book_ticket = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, proceed_id))
            )
            # Move to the "Proceed" button and click it
            actions.move_to_element(book_ticket).perform()
            # Another human-like delay before proceeding
            human_delay()
            book_ticket.click()

            # Locate the login button (if user needs to login) and wait until it becomes clickable
            login_id = "//*[@id='homedelivery-login-to-proceed-button']"
            login = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, login_id))
            )

            # Move to the login button and click it
            actions.move_to_element(login).perform()
            human_delay()
            login.click()


        except (NoSuchElementException, TimeoutException) as e:
            print("Encountered an error while booking tickets:", e)
            attempts += 1
            if not reload(driver, max_retry):
                print("Unable to recover from the error. Exiting.")
                break
            else:
                print("Retrying to book tickets after reload...")


def try_booking_tickets(driver, reservation_time, number_of_tickets, max_attempts=1000, start_time=dt_time(10, 0),
                        end_time=dt_time(23, 59)):
    attempt = 1
    while attempt <= max_attempts:
        current_time = datetime.now().time()
        if not is_within_time_range(start_time, end_time):
            print(f"Current time {current_time} is outside the specified range {start_time} to {end_time}. Waiting...")
            time.sleep(1)  # Sleep before checking again
            continue

        print(f"Attempt {attempt} to book tickets at {current_time}...")
        try:
            book_tickets(driver, number_of_tickets)
            print("Booking completed successfully!")
            break
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Attempt {attempt} failed. Error: {e}")
            if not reload(driver):
                print("Failed to reload the page. Exiting.")
                break
            else:
                print("Retrying booking after reload...")
                attempt += 1
                time.sleep(1)  # Slight delay before the next attempt


# Main function to execute the script
def main():
    driver = init_driver("chromedriver.exe")

    try:
        open_bookmyshow(driver)
        city = input("Enter the city: \n")
        enter_city(driver, city)
        human_delay(2, 3)
        click_event_link(driver, "Events")
        event_name = input("Enter the event where you want to go \n")
        click_movie_link(driver, event_name)
        number_of_tickets = int(input("Enter the Number of tickets \n"))

        # Specify the reservation time range and attempt to book tickets
        start_time = dt_time(9, 20)  # Start time for booking
        end_time = dt_time(23, 59)  # End time for booking
        try_booking_tickets(driver, reservation_time=None, number_of_tickets=number_of_tickets, max_attempts=1000,
                            start_time=start_time, end_time=end_time)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
