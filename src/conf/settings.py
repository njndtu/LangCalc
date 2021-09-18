import logging.config
import git
import os

# Logging config
logging.basicConfig(level=logging.INFO)









# Global constants
LANG_CALC_PATH = git.Repo('.', search_parent_directories=True).working_tree_dir

DATA_PATH = os.path.join(LANG_CALC_PATH, "data")


UPDATE_HEROES = False

UPDATE_TROOPS = False

UPDATE_SKILLS = True

UPDATE_EQUIP = True





