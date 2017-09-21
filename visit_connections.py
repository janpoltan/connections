#pylint: disable=invalid-name
"""
Visit people you may know in LinkedIn
"""
import time
import sys
from random import randint
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Firefox()
contacts_found = {}

def do_visit(username, password):
    """Visits the profile under People you may know"""
    if username is None or password is None:
        sys.exit('username and pasword is require')

    do_login(username, password)
    
    go_to_mynetwork_page()

    # TODO: Way to check if the my network page was fully loaded
    # Thus driver.get waits if the page was loaded ?
    
    profile_list = driver.find_elements_by_class_name('mn-pymk-list__card')
    last_total_profiles = 0
    total_profiles = len(profile_list)

    add_profile_to_visit(profile_list)

    while True:
        # Loads the other profile
        simulate_press_end()

        # gives time to load the other profile
        # TODO: Use driver wait when presence of all elements ?
        simulate_pause()

        profile_list = driver.find_elements_by_class_name('mn-pymk-list__card')
        total_profiles = len(profile_list)
        if total_profiles == last_total_profiles:
            break
        else:
            last_total_profiles = total_profiles
            add_profile_to_visit(profile_list)
    
    print 'Total profiles found: %s' % len(contacts_found)


def do_login(username, password):
    """Logs in to the page"""
    driver.get('https://www.linkedin.com/')
    assert 'LinkedIn' in driver.title
    elem = driver.find_element_by_name("session_key")
    elem.clear()
    elem.send_keys(username)
    elem = driver.find_element_by_name("session_password")
    elem.clear()
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)

def go_to_mynetwork_page():
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'mynetwork-tab-icon'))
    )
    driver.get('https://www.linkedin.com/mynetwork/')

def simulate_press_end():
    ActionChains(driver).key_down(Keys.COMMAND).send_keys(Keys.ARROW_DOWN).perform()

def add_profile_to_visit(profile_list_elem):
    for profile in profile_list_elem:
        profile_link_elem = profile.find_element_by_class_name('mn-person-info__link')
        person_info = profile.find_element_by_class_name('mn-person-info__name')
        ember_id = profile_link_elem.get_attribute('id')
        profile_name = person_info.get_attribute('innerHTML').encode('utf-8').strip()
        profile_link = profile_link_elem.get_attribute('href').encode('utf-8').strip()
        if contacts_found.has_key(ember_id) is False:
            contacts_found[ember_id] = {
                u'profile_name': profile_name,
                u'profile_link': profile_link
            }

def simulate_pause():
    """Simulates a pause"""
    time.sleep(randint(5, 8))
