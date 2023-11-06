import os
from time import sleep
from tqdm import tqdm
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


## DEFINITIONS
class VisaSubClass:

    section_xpath = '//*[@id="tab-pane-1"]/ha-visa-details-root/div/form/div[2]/div[1]/ha-tab-strip/div[1]/ul/li[{i}]/a'
    section_mapper = {
        'overview': 1,
        'about': 2,
        'eligibility': 3,
        'step_by_step': 4,
        'when_you_have_applied': 5
    }

    def __init__(self, url, driver):
        self.url = url
        self.driver = driver
        self.visa_name = self.url.split('/')[-1]
        
    def retrieve_all_sections(self):
        self.driver.get(url)
        sleep(.5)
        self.source = {}

        for name, index in tqdm(self.section_mapper.items()):
            self.driver.find_element_by_xpath(self.section_xpath.format(i=index)).click()
            sleep(.5)
            self.source[name] = self.driver.page_source
        
    def save(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

        for section, content in self.source.items():
            with open(f'{directory}/{self.visa_name}_{section}.html', 'wb') as f:
                f.write(str(content).encode('utf-8'))


## RUNTIME
if __name__ == '__main__':
    
    directory = '../data'
    with open('urls.txt', 'r', encoding='utf8') as f:
        urls = f.read()
        urls = urls.split('\n')

    driver = webdriver.Chrome(ChromeDriverManager().install())
    for url in tqdm(urls):
        visa = VisaSubClass(url, driver)
        try:
            visa.retrieve_all_sections()
            visa.save(directory)
        except:
            print(f'Failed to retrieve {visa.visa_name}')
            visa.source = {'about': visa.driver.page_source}
            visa.save(directory)
        
    driver.close()
    print('Finished!')
