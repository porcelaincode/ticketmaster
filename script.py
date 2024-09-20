import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from threading import Event
from multiprocessing import Process
import pika

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

with open('config.json', 'r') as f:
    config = json.load(f)

base_url = config['base_url']
number_of_instances = config['number_of_instances']
steps = config['steps']
payment_type = config['payment_preferred_type']

drivers = {}
driver_ready_event = Event()


def start_driver(driver_id):
    options = Options()
    options.headless = True  # Saves a bunch of memory
    driver = webdriver.Chrome(service=Service(
        "/path/to/chromedriver"), options=options)
    drivers[driver_id] = driver

    logger.info(f"Driver {driver_id} started and navigating to {base_url}")
    driver.get(base_url)

    for step in steps:
        action = step['action']
        locator = step['locator']
        element = None

        if locator['type'] == 'text':
            element = driver.find_element(
                By.XPATH, f"//*[contains(text(), '{locator['value']}')]")
        elif locator['type'] == 'css':
            element = driver.find_element(By.CSS_SELECTOR, locator['value'])

        if action == "click":
            element.click()
        elif action == "input":
            element.send_keys(step['value'])
        elif action == "wait":
            time.sleep(step['time'])

        logger.info(f"Driver {driver_id} performed action: {action}")

        if 'Payment' in element.text:
            logger.info(f"Driver {driver_id} has reached the payment page.")
            emit_event('payment_ready')
            break

    driver_ready_event.set()


def emit_event(event_name):
    """Emit event via RabbitMQ."""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=event_name)
    channel.basic_publish(exchange='', routing_key=event_name, body=event_name)
    connection.close()


def handle_payment(driver_id):
    driver = drivers.get(driver_id)
    if driver:
        payment_button = driver.find_element(
            By.XPATH, f"//*[contains(text(), 'Payment')]")
        payment_button.click()
        logger.info(f"Driver {driver_id} clicked Payment button")
        emit_event('payment_initiated')


def destroy_drivers(except_id=None):
    for driver_id, driver in drivers.items():
        if driver_id != except_id:
            driver.quit()
            logger.info(f"Destroyed driver {driver_id}")
    drivers.clear()


def main():
    try:
        processes = []
        for i in range(number_of_instances):
            p = Process(target=start_driver, args=(i,))
            processes.append(p)
            p.start()

        driver_ready_event.wait()

        destroy_drivers(except_id=0)
        handle_payment(0)

        logger.info("Sleeping for 60 minutes after payment initiation")
        time.sleep(3600)

    except KeyboardInterrupt:
        logger.info("Program interrupted. Exiting gracefully...")
        destroy_drivers()
        for p in processes:
            p.terminate()
            p.join()


if __name__ == "__main__":
    main()