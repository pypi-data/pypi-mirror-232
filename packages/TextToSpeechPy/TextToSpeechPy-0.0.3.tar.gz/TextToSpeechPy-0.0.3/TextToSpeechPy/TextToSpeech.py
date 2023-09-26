import pyttsx3,time,warnings

#selenium version should be latest or  more than 4.12.*
from selenium.webdriver.support.ui import Select

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

warnings.filterwarnings("ignore", category=UserWarning, module="module_name")


#crome Based




# Create Chrome options
chrome_options = Options()
chrome_options.add_argument('--log-level=3')
chrome_options.headless =True

# Create a Chrome WebDriver instance with the specified options
driver = webdriver.Chrome(options=chrome_options)

# Maximize the browser window
driver.maximize_window()

# Define the URL to visit
url = "https://ttsmp3.com/text-to-speech/British%20English/"

# Navigate to the URL
driver.get(url)

ButtonSelection=Select(driver.find_element(by=By.XPATH,value='html/body/div[4]/div[2]/form/select'))
ButtonSelection.select_by_visible_text('British English / Brian')

def  speak_chrome(msg):
    lengthofText=len(str(msg))
    if lengthofText==0:
        pass
    else:
        print(f'\nAI : {msg}\n') 
        Data=str(msg)
        xpathofsec='/html/body/div[4]/div[2]/form/textarea'
        driver.find_element(By.XPATH,value=xpathofsec).send_keys(Data)
        driver.find_element(By.XPATH,value='//*[@id="vorlesenbutton"]').click()
        print('waiting for voice........')
        # Calculate sleep duration based on message length
        print(lengthofText)
        if lengthofText<=30:
            time.sleep(8)
            print('bac')
        elif lengthofText >= 30:
            time.sleep(7)
        elif lengthofText >= 40:
            time.sleep(8)
        
        elif lengthofText >= 55:
            time.sleep(10)
        elif lengthofText >= 70:
                time.sleep(11)
        elif lengthofText >= 100:
            time.sleep(13)
        elif lengthofText >= 120:
            time.sleep(15)
        else:
            time.sleep(2)

        driver.find_element(By.XPATH,value=xpathofsec).clear()

def textToSpeechAdvance(message, language):
    """
    Converts a text message to speech using the TTS Converter website.

    Args:
        message (str): The text message you want to convert to speech.
        language (str): The language in which you want the speech output ('hindi' or 'English').

    Returns:
        None

    Note:
        Make sure to have the appropriate WebDriver (e.g., Selenium) set up before using this function.

    Example:
        textToSpeechAdvance("Hello, how are you?", "English")
    """
    driver.get(url='https://ttsconverter.io/')
    driver.find_element(by=By.XPATH, value="//span[@class='select2-selection__arrow']").click()
    time.sleep(5)
    Hindi = driver.find_element(by=By.XPATH, value="//span[@class='select2-container select2-container--default select2-container--open']/span/span[2]/ul/li[66]/span")
    English = driver.find_element(by=By.XPATH, value="//span[@class='select2-container select2-container--default select2-container--open']/span/span[2]/ul/li[50]/span")
    lang = language
    if lang == 'hindi':
        Hindi.click()
    if lang == 'English':
        English.click()
    driver.find_element(by=By.XPATH, value="//textarea[@class='form-control text_input']").send_keys(message)
    driver.find_element(by=By.ID, value='radioPrimaryhi-IN-Standard-B').click()
    play = driver.find_element(by=By.XPATH, value="//a[@class='btn btn-lg btn-primary mt-1 convert-now']")
    play.click()
    time.sleep(5)






