import requests
from lxml.html import fromstring
import os
import logging
from conf.settings import (
UPDATE_HEROES,
UPDATE_TROOPS,
UPDATE_SKILLS,
UPDATE_EQUIP
)
from utils import save_as_jsonl


ALL_HEROES_URL = "https://wiki.biligame.com/langrisser/%E8%8B%B1%E9%9B%84%E6%95%B0%E6%8D%AE%E8%A1%A8"
ALL_TROOPS_URL = "https://wiki.biligame.com/langrisser/%E5%85%B5%E7%A7%8D%E5%9B%BE%E9%89%B4"
ALL_SKILLS_URL = "https://wiki.biligame.com/langrisser/%E6%8A%80%E8%83%BD%E6%95%B0%E6%8D%AE%E8%A1%A8"
ALL_EQUIP_URL = "https://wiki.biligame.com/langrisser/%E8%A3%85%E5%A4%87%E5%9B%BE%E9%89%B4"
BASE_URL = "https://wiki.biligame.com"




logger = logging.getLogger(__name__)

def update_heroes():
    '''
    returns:
        all_heroes (list[json]) : a list of heroes in json form, differentiated by name and branch. 
        all_factions (set[str]) : a set of all factions
    '''
    all_factions = set()
    all_heroes = []
    resp = requests.get(ALL_HEROES_URL, headers = {'User-Agent' :  'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'} )
    source = fromstring(resp.content)
    path = "//tbody"
    heroes = source.xpath(path)[1]
    first = True
    for hero in heroes:
        if first:
            first = False
            continue
        try:
            # basic stats
            stats = (hero.text_content())    
            stats = [i for i in (stats.split("\n")) if i != "" ]
            # hp atk int def mdef skill move range
            to_track = ["name","branch", "hp", "atk", "int", "def", "mdef", "skill", "move", "range"]
            hero_info = {}
            for idx,stat in enumerate(stats):
                hero_info[to_track[idx]] = int(stat) if stat.isnumeric() else str(stat)
            
            info = hero.attrib
            rarity = info['data-param1']
            hero_factions = [i.strip() for i in info['data-param2'].split(",")]
            for faction in hero_factions:
                all_factions.add(faction)
            hero_class = info['data-param3']
            hero_info["rarity"] = rarity
            hero_info["factions"] = hero_factions
            hero_info["class"] = hero_class

            links = [i for i in hero.iterlinks()]
            hero_info["url"] = BASE_URL + links[0][-2]
            hero_info["pic"] = links[1][-2] 

            # getting troop bonuses

            resp = requests.get(hero_info['url'], headers = {'User-Agent' :  'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'} )
            source = fromstring(resp.content)

            path = "//td[@class='bg_red']" # first 4 red bars, need to change this down the line
            troop_bonus_path = source.xpath(path)[:4]
            troop_bonus = []
            for i in troop_bonus_path:
                troop_bonus.append(i.text_content())
                # atk hp def mdef 
            hero_info["troop_bonus"] = troop_bonus
            all_heroes.append(hero_info)
            logger.info(hero_info)
            # hero talent gotta be hand input :(
        except Exception as e:
            logger.warning("Erroneous hero : %s" % stats)
            logger.warning("Error occured doing hero parsing from wiki : %s" % (e))
    logger.info("Completed hero scrapping")
    
    return all_heroes, all_factions

def update_troops():
    '''
    returns:
        all_troops (list[json]) : returns list of json objects representing troop info
    '''
    all_troops = []

    resp = requests.get(ALL_TROOPS_URL, headers = {'User-Agent' :  'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'} )
    source = fromstring(resp.content)
    path = "//tbody/tr/td/div[@style='float:left;marign:5px']/div/div/a"
    troops = source.xpath(path)
    for troop in troops:
        info = troop.attrib
        troop_info = {}
        troop_info['name'] = info['title']
        troop_info['url'] = BASE_URL + info['href']

        resp = requests.get(troop_info['url'], headers = {'User-Agent' :  'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'} )
        source = fromstring(resp.content)

        path = "//table/tbody/tr"
        info_path = source.xpath(path)[:5]
        troop_stat = []
        for i in info_path:
            row = [j for j in (i.text_content().split("\n")) if j != ""]
            troop_stat+=row

        for idx in range(len(troop_stat)//2):
            troop_info[troop_stat[2*idx]] = troop_stat[2*idx+1]


        path = "//tr/td/div/div/div/a"
        used_by_path =  source.xpath(path)
        used_by = []
        for i in used_by_path:
            hero = (i.attrib)['title']
            used_by.append(hero)

        troop_info['used_by'] = used_by

        logger.info("troop info : %s" % troop_info)


        path = "//a[@class='image']"
        pic_url = source.xpath(path)[0].attrib['href']
        troop_info['pic'] = BASE_URL + pic_url
        all_troops.append(troop_info)

        logger.info(troop_info)
    logger.info("Completed troop scrapping")
    return all_troops

def update_equip():
    all_equip = []

    resp = requests.get(ALL_EQUIP_URL, headers = {'User-Agent' :  'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'} )
    source = fromstring(resp.content)
    path = "//tbody"
    equips = source.xpath(path)
    print(equips)
    for equip in equips:
        print(equip.attrib)


if __name__ == "__main__":
    if UPDATE_HEROES:
        logger.info("Updating heroes")
        all_heroes , all_factions = update_heroes()
        save_as_jsonl(all_heroes, "all_heroes.jsonl")
        save_as_jsonl(all_factions, "all_factions.jsonl")

    if UPDATE_TROOPS:
        logger.info("Updating troops")
        save_as_jsonl(update_troops(), "all_troops.jsonl")

    if UPDATE_SKILLS:
        logger.info("Updating skills")
        save_as_jsonl(update_skills(), "all_skills.jsonl")

    quit()

    if UPDATE_EQUIP:
        logger.info("Updating equip")
        save_as_jsonl(update_equip(), "all_equip.jsonl")