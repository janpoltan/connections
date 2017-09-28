#pylint: disable=invalid-name
"""
Visit people you may know in LinkedIn
"""
import time
import sys
import pickle
import os
from random import randint
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CONTACTS_FILE_PATH = 'contacts.p'

driver = webdriver.Firefox()
contacts_found = {}
exclude_contacts = []

def load_contacts():
    global contacts_found
    if os.path.exists(CONTACTS_FILE_PATH):
        contacts_found = pickle.load(open(CONTACTS_FILE_PATH, 'rb'))

def save_contacts():
    pickle.dump(contacts_found, open(CONTACTS_FILE_PATH, 'wb'))

def do_visit(username, password, excluded):
    global exclude_contacts
    """Visits the profile under People you may know"""
    if username is None or password is None:
        sys.exit('username and pasword is require')

    exclude_contacts = excluded
    
    load_contacts()

    do_login(username, password)

    # This loads the profiles in the my connections
    go_to_my_connections()
    get_connections()
    
    go_to_mynetwork_page()

    # TODO: Way to check if the my network page was fully loaded
    # Does driver.get waits if the page was loaded ?
    
    profile_list = driver.find_elements_by_class_name('mn-pymk-list__card')
    last_total_profiles = 0
    total_profiles = len(profile_list)

    add_profile_to_visit(profile_list)

    # This loads the profiles in the 'People you may know'
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
    visit_profiles()

    save_contacts()
    driver.close()


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
        add_to_contacts(ember_id, profile_name, profile_link)

def visit_profiles():
    total_found = len(contacts_found)
    if total_found > 0:
        for key, value in contacts_found.iteritems():
            contact_name = value.get('profile_name')
            contact_link = value.get('profile_link')
            try:
                # TODO: Refactor this, proper way to exclude an item
                excluded = False
                total_exclude_contacts = len(exclude_contacts)
                if total_exclude_contacts > 0:
                    for ex in exclude_contacts:
                        if contact_name.lower().find(ex) == -1:
                            continue
                        else:
                            excluded = True
                            break
                else:
                    print 'Exclude list is empty'

                if not excluded:
                    visit_profile(contact_name, contact_link)
                else:
                    print 'Skipping ', contact_name
            except:
                driver.close()
                print "Unexpected error: ", sys.exc_info()[0]
            finally:
                simulate_pause(start=1, end=5)


def visit_profile(contact_name, contact_link):
    print 'Visiting ', contact_name
    driver.get(contact_link)
    simulate_pause(start=1, end=4)
    simulate_press_end()
    simulate_pause(start=2, end=5)

def simulate_pause(start=5, end=8):
    """Simulates a pause"""
    time.sleep(randint(start, end))

def go_to_my_connections():
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'mynetwork-tab-icon'))
    )
    driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    simulate_pause(1,5)

def get_connections():
    try:
        # TODO: Need to check on connections paging
        connections = driver.find_elements_by_class_name('mn-person-card')        
        for conn in connections:
            anchor = conn.find_element_by_class_name('mn-person-info__picture')
            ember_id = anchor.get_attribute('id')
            profile_link = anchor.get_attribute('href')            
            name = conn.find_element_by_class_name('mn-person-info__name')
            profile_name = name.get_attribute('innerHTML').encode('utf-8').strip()
            add_to_contacts(ember_id, profile_name, profile_link)
    except:
        print 'Error getting connections container class connection-card"'
    
    finally:
        simulate_pause(1,5)

def add_to_contacts(ember_id, profile_name, profile_link):
    if contacts_found.has_key(ember_id) is False:
        contacts_found[ember_id] = {
            u'profile_name': profile_name,
            u'profile_link': profile_link
        }
