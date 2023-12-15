from time import sleep
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
import csv
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select


# Set up the WebDriver
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

# Firefox options
options = FirefoxOptions()
# options.add_argument("--headless")  # This sets the headless option
options.set_preference("general.useragent.override", user_agent)


# Initialize the driver with both Selenium Wire and Firefox options
driver = webdriver.Firefox(options=options,service=Service(GeckoDriverManager().install()), )

# Function to extract table rows and write to CSV
def extract_data_to_csv(writer):
    table = driver.find_element(By.ID, "data-table")
    rows = table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        data = [td.text for td in row.find_elements(By.TAG_NAME, "td")]
        if data:
            writer.writerow(data)

# Open the website
driver.get("https://mondego.ics.uci.edu/projects/SourcererJBF/jaigantic.html")
driver.maximize_window()
sleep(10)
# Locate the element by its text
stars_column_header = driver.find_element(By.XPATH, "//th[contains(text(), 'Stars')]")

# Click on the element twice
stars_column_header.click()
sleep(0.5)  # A brief pause between clicks
stars_column_header.click()
select_element = driver.find_element(By.NAME, "data-table_length")

# Create a Select object for the located select element
select_object = Select(select_element)

# Select the option with value "100"
select_object.select_by_value("100")

# Open CSV file to write
with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)

    # Process each page
    for page in range(1, 4016):
        print(f"Processing page {page}")
        extract_data_to_csv(writer)

        # Navigate to the next page
        try:
            next_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Next')]")  # Find the next button
            next_button.click()
            sleep(1)  # Wait for the page to load
        except NoSuchElementException:
            print("Next page not found. Exiting.")
            break

# Close the browser
driver.quit()