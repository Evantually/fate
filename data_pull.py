from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
import urllib.request
from urllib.error import HTTPError
from app.models import ProfessionItem, ProfessionIngredient, RecipeIngredient, DescriptionText
import os
import csv
from app import db

def gatherProfessionInfo(db):

    def cleanMouseOver(elem):
        return elem.get_attribute('onmouseover').split("'")[1]

    def getPictureLink(elem):
        return elem.get_attribute('src')

    def itemQuality(elem):
        i_quality = ''
        try:
            elem.find_element_by_class_name('greenname')
            i_quality = 'Uncommon'
        except:
            pass
        try:
            elem.find_element_by_class_name('bluename')
            i_quality = 'Rare'
        except:
            pass
        try:
            elem.find_element_by_class_name('purplename')
            i_quality = 'Epic'
        except:
            pass
        if i_quality == '':
            i_quality = 'Common'
        return i_quality
    
    def descriptionText(elem):
        d_text = ''
        if internal_id == 'id0':
            d_text = 'None'
            return d_text
        try:
            OWN_TEXT_SCRIPT = """var el=arguments[0];var child=el.firstChild;var texts=[]; while(child){if(child.nodeType == 3){texts.push(child.data);}child=child.nextSibling;}var text=texts.join("");return text;"""
            d_text = browser.execute_script(OWN_TEXT_SCRIPT, elem)
        except:
            pass
        text_lines = d_text.split('\n')
        for index, text in enumerate(text_lines):
            text_lines[index] = ' '.join(text.split('\xa0'))
        filtered_text = list(filter(('').__ne__, text_lines))
        return filtered_text
    
    def itemSlot(desc_text):
        desc_text = [d.lower() for d in desc_text]
        slot = ''
        if 'feet' in desc_text:
            slot = 'Feet'
        elif 'hands' in desc_text:
            slot = 'Hands'
        elif 'main hand' in desc_text:
            slot = 'Main Hand'
        elif 'one-hand' in desc_text:
            slot = 'One-Hand'
        elif 'Two-Hand' in desc_text:
            slot = 'Two-Hand'
        elif 'chest' in desc_text:
            slot = 'Chest'
        elif 'shoulder' in desc_text:
            slot = 'Shoulder'
        elif 'wrist' in desc_text:
            slot = 'Wrist'
        elif 'legs' in desc_text:
            slot = 'Legs'
        elif 'waist' in desc_text:
            slot = 'Waist'
        elif 'off hand' in desc_text:
            slot = 'Off Hand'
        elif 'head' in desc_text:
            slot = 'Head'
        elif 'trinket' in desc_text:
            slot = 'Trinket'
        elif 'shirt' in desc_text:
            slot = 'Shirt'
        elif 'tabard' in desc_text:
            slot = 'Tabard'
        elif 'finger' in desc_text:
            slot = 'Finger'
        elif 'back' in desc_text:
            slot = 'Back'
        elif 'neck' in desc_text:
            slot = 'Neck'
        return slot


    browser = initialize()
    profs = [ ('https://web.archive.org/web/20060414194323/http://wow.allakhazam.com/db/skill.html?line=171', 'Alchemy')
            ,('https://web.archive.org/web/20060414191413/http://wow.allakhazam.com/db/skill.html?line=164', 'Blacksmithing')
            ,('https://web.archive.org/web/20060412210635/http://wow.allakhazam.com/db/skill.html?line=333', 'Enchanting')
            ,('https://web.archive.org/web/20060414194356/http://wow.allakhazam.com/db/skill.html?line=202', 'Engineering')
            ,('https://web.archive.org/web/20060412210622/http://wow.allakhazam.com/db/skill.html?line=165', 'Leatherworking')
            ,('https://web.archive.org/web/20060501123450/http://wow.allakhazam.com:80/db/skill.html?line=197', 'Tailoring')]
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
                    tds[1].find_element_by_tag_name('small').get_attribute('innerText')
                    learned_from = 'recipe'
                except NoSuchElementException:
                    learned_from = 'trainer'
                try:
                    skill_required = int(tds[3].get_attribute('innerText'))
                except ValueError:
                    skill_required = 0
                if internal_id != 'id0':
                    item_info = browser.find_element_by_id(internal_id)
                    description_text = descriptionText(item_info.find_element_by_class_name('wowitem'))
                    item_quality = itemQuality(item_info)
                    try:
                        armor_class = item_info.find_element_by_class_name('wowrttxt').get_attribute('innerText')
                    except:
                        armor_class = 'None'
                    item_slot = itemSlot(description_text)
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
                                                item_quality=item_quality, armor_class=armor_class,
                                                item_slot=item_slot, action=action, result=result)
                    for desc in description_text:
                        res_desc = DescriptionText.query.filter_by(item_id=profession_item.id, text=desc).first()
                        if res_desc is None:
                            description = DescriptionText(item_id=profession_item.id, text=desc)
                            db.session.add(description)
                        else:
                            res_desc.item_id = profession_item.id
                            res_desc.text = desc
                            db.session.commit()
                    db.session.add(profession_item)
                    db.session.commit()
                else:
                    for desc in description_text:
                        description = DescriptionText(item_id=profession_item.id, text=desc)
                        db.session.add(description)
                    profession_item = ProfessionItem.query.filter_by(internal_id=internal_id).first()
                    profession_item.profession = profession
                    profession_item.internal_id = internal_id
                    profession_item.name = name
                    profession_item.learned_from = learned_from
                    profession_item.skill_required = skill_required
                    profession_item.item_quality = item_quality
                    profession_item.armor_class = armor_class
                    profession_item.item_slot = item_slot
                    profession_item.action = action
                    profession_item.result = result
                    profession_item.image_link = image_link
                    db.session.commit()
                ingredients = tds[4].get_attribute('innerText').split(',')
                ings = tds[4].find_elements_by_tag_name('a')
                for index, ingredient in enumerate(ingredients):
                    quantity = ingredient.split('x')[0]
                    pi_name = ings[index].find_element_by_tag_name('font').get_attribute('innerText')
                    pi_internal_id = cleanMouseOver(ings[index])
                    pi_item_info = browser.find_element_by_id(pi_internal_id)
                    pi_item_quality = itemQuality(pi_item_info)
                    try:
                        pi_item_type = pi_item_info.find_element_by_class_name('wowrttxt').get_attribute('innerText')
                    except:
                        pi_item_type = 'None'
                    profession_ingredient = ProfessionIngredient.query.filter_by(internal_id=pi_internal_id).first()
                    if profession_ingredient is None:
                        profession_ingredient = ProfessionIngredient(name=pi_name, internal_id=pi_internal_id, item_quality=pi_item_quality, item_type=pi_item_type)
                        db.session.add(profession_ingredient)
                        db.session.commit()
                    else:
                        profession_ingredient.name = pi_name
                        profession_ingredient.internal_id = pi_internal_id
                        profession_ingredient.item_quality = pi_item_quality
                        profession_ingredient.item_type = pi_item_type
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

def initialize():
#    option = webdriver.ChromeOptions()
#    option.add_argument("--incognito")
#    option.add_argument("--window-size=1440,800")
    options = Options()
    options.headless = True
    binary = FirefoxBinary(os.environ.get('FIREFOX_BIN'))
    browser = webdriver.Firefox(executable_path=os.environ.get('GECKODRIVER_PATH'), firefox_binary=binary, options=options)
    return browser

def fillDatabase():
    with open('description-text.csv') as f:
        lines = csv.reader(f, delimiter=',')
        for row in lines:
            db.session.add(DescriptionText(text=row[1], item_id=int(row[2])))
        db.session.commit()
    with open('profession-item.csv') as f:
        lines = csv.reader(f, delimiter=',')
        for row in lines:
            db.session.add(ProfessionItem(profession=row[1], image_link=row[2], internal_id=row[3],
                            name=row[4], learned_from=row[5], skill_required=int(row[6]), item_quality=row[7],
                            armor_class=row[8], item_slot=row[9], action=row[10], result=int(row[11])))
        db.session.commit()
    with open('recipe-ingredient.csv') as f:
        lines = csv.reader(f, delimiter=',')
        for row in lines:
            db.session.add(RecipeIngredient(item_id=int(row[1]), ingredient_id=int(row[2]), quantity=int(row[3])))
        db.session.commit()
