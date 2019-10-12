from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import urllib.request
from urllib.error import HTTPError
from app.models import ProfessionItem, ProfessionIngredient, RecipeIngredient

def gatherProfessionInfo(db):

    def initialize():
    #    option = webdriver.ChromeOptions()
    #    option.add_argument("--incognito")
    #    option.add_argument("--window-size=1440,800")
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.privatebrowsing.autostart", True)
        browser = webdriver.Firefox(executable_path='geckodriver.exe', firefox_profile=profile)
        return browser

    def cleanMouseOver(elem):
        return elem.get_attribute('onmouseover').split("'")[1]

    def getPictureLink(elem):
        return elem.get_attribute('src')

    browser = initialize()
    profs = [ #('https://web.archive.org/web/20060414194323/http://wow.allakhazam.com/db/skill.html?line=171', 'Alchemy')
            #,('https://web.archive.org/web/20060414191413/http://wow.allakhazam.com/db/skill.html?line=164', 'Blacksmithing')
            ('https://web.archive.org/web/20060412210635/http://wow.allakhazam.com/db/skill.html?line=333', 'Enchanting')
            #,('https://web.archive.org/web/20060414194356/http://wow.allakhazam.com/db/skill.html?line=202', 'Engineering')
            #,('https://web.archive.org/web/20060412210622/http://wow.allakhazam.com/db/skill.html?line=165', 'Leatherworking')
            #,('https://web.archive.org/web/20060501123450/http://wow.allakhazam.com:80/db/skill.html?line=197', 'Tailoring')]
    delay = 10

    for prof in profs:
        browser.get(prof[0])
        WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        trs = browser.find_elements_by_tag_name('tr')
        for index, tr in enumerate(trs):
            print(f'On entry {index} of {len(trs)}.')
            try:
                tds = tr.find_elements_by_tag_name('td')
                profession = prof[1]
                internal_id = cleanMouseOver(tds[1].find_element_by_tag_name('a'))
                name = tds[1].find_element_by_tag_name('a').get_attribute('innerText')
                try:
                    urllib.request.urlretrieve(getPictureLink(tds[0].find_element_by_tag_name('img')), f"app/static/imgs/{prof[1]}/{cleanMouseOver(tds[1].find_element_by_tag_name('a'))}.png")
                    image_link = f"imgs/{prof[1]}/{cleanMouseOver(tds[1].find_element_by_tag_name('a'))}.png"
                except HTTPError as e:
                    print(e)
                    image_link = f"app/static/imgs/Alchemy/id21546.png"
                try:
                    tds[1].find_element_by_id('span').get_attribute('innerText')
                    learned_from = 'recipe'
                except:
                    learned_from = 'trainer'
                try:
                    skill_required = int(tds[3].get_attribute('innerText'))
                except ValueError:
                    skill_required = 0
                try:
                    if internal_id == 'id0':
                        pass
                    else:
                        action = browser.find_element_by_id(internal_id).find_element_by_class_name('itemeffectlink').get_attribute('innerText')
                except:
                    if internal_id == 'id0':
                        pass
                    else:
                        action = browser.find_element_by_id(internal_id).find_element_by_class_name('iname').get_attribute('innerText')
                try:
                    result = int(tds[5].get_attribute('innerText').split('x')[0])
                except:
                    result = ''
                if ProfessionItem.query.filter_by(internal_id=internal_id).first() is None:
                    profession_item = ProfessionItem(profession=profession, image_link=image_link,
                                                internal_id=internal_id, name=name, 
                                                learned_from=learned_from, skill_required=skill_required,
                                                action=action, result=result)
                    db.session.add(profession_item)
                    db.session.commit()
                else:
                    profession_item = ProfessionItem.query.filter_by(internal_id=internal_id).first()
                    profession_item.image_link = image_link
                    db.session.commit()
                ingredients = tds[4].get_attribute('innerText').split(',')
                ings = tds[4].find_elements_by_tag_name('a')
                for index, ingredient in enumerate(ingredients):
                    quantity = ingredient.split('x')[0]
                    name = ings[index].find_element_by_tag_name('font').get_attribute('innerText')
                    internal_id = cleanMouseOver(ings[index])
                    profession_ingredient = ProfessionIngredient.query.filter_by(internal_id=internal_id).first()
                    if profession_ingredient is None:
                        profession_ingredient = ProfessionIngredient(name=name, internal_id=internal_id)
                        db.session.add(profession_ingredient)
                        db.session.commit()
                    if RecipeIngredient.query.filter_by(item_id=profession_item.id, 
                                                        ingredient_id=profession_ingredient.id, 
                                                        quantity=quantity).first() is None:
                        recipe_ingredient = RecipeIngredient(item_id=profession_item.id,
                                                            ingredient_id=profession_ingredient.id,
                                                            quantity=quantity)
                        db.session.add(recipe_ingredient)
                        db.session.commit()
            except (AttributeError, NoSuchElementException, IndexError) as e:
                print(repr(e))
                continue
    db.session.commit()
    browser.quit()