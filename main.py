from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pymongo import MongoClient
from selenium.webdriver.chrome.options import Options

client = MongoClient('mongodb+srv://parthkapoor488:lv0j55TlWQLs03tY@cluster0.ibgca.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['food_database']
collection = db['food_items']


foodList =  ['red creamy pasta']
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument("--disable-gpu")  # Applicable only for Windows OS, but safe to add
chrome_options.add_argument("--remote-debugging-port=9222")  # Required for headless mode
chrome_options.add_argument("--window-size=1920,1080")  # Set window size to avoid resolution issues

driver = webdriver.Chrome(chrome_options)

for foodItem in foodList:

    try:
        driver.get("https://www.bonhappetee.com/food-search/search-page?utm_medium=paid&utm_source=Google&utm_campaign=DK_TOFU_Search_Leads_0601&utm_term=recipe+database&gclid=CjwKCAjwreW2BhBhEiwAavLwfK80FatwojVjRk0Ko0-REHRrxQIdB_iOGCW1bw0P-iBSlQhtU0MBDRoCDFYQAvD_BwE")

        search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'searchInput-2')))
        search.send_keys(foodItem)
        time.sleep(4) 
        button = driver.find_element(By.XPATH, '//*[@id="searchfood_button"]')
        button.click()

        json_objects = []
        keys = ["item_name", "carbs", "protein", "fat", "calories"]

        for i in range(2, 12):
            try:
                section = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//*[@id="sr-container"]/div[{i}]'))
                )
                elements = driver.find_elements(By.XPATH, f'//*[@id="sr-container"]/div[{i}]')
                for element in elements:
                    lines = element.text.split('\n')

                    try:
                        dish_name = lines[0].split(",")[0]
                        carbs = lines[1].split()[1]
                        protein = lines[2].split()[1] 
                        fat = lines[3].split()[1]  
                        calories = lines[4].split()[0] 

                        existing_data = collection.find_one({"item_name" : dish_name})
                        if not existing_data:
                            json_data = {
                            "item_name": dish_name,
                            "carbs": carbs,
                            "protein": protein,
                            "fat": fat,
                            "calories": calories
                            }

                            json_objects.append(json_data)

                    except IndexError:
                        print(f"Error parsing item data in section {i}. Skipping item.")

            except TimeoutException:
                print(f"Timed out while waiting for section {i}.")

        if json_objects:
            collection.insert_many(json_objects)
            print(f"Inserted {len(json_objects)} items into MongoDB")
        else:
            print("No data to insert")

    except TimeoutException:
        print("Page load timed out after 10 seconds")

        time.sleep(5)

driver.quit()
