from utils.connection import connection
from utils.queries import ind_quest_KR, ind_quest_HR
from config import DATE_TO,TABLE,DATE_FROM,YEAR_STRING,DATE_TO_MIN1,DATE_FROM_MIN1,YEAR_STRING_MIN1,PREVIOUS_TABLE
import pandas as pd

def individual_questions_kr_table():

    cnxn = connection('PROMS_DEVELOPMENT')
    indquests_kr = pd.read_sql(ind_quest_KR(DATE_TO,DATE_FROM, YEAR_STRING,TABLE),cnxn)
    return indquests_kr

def individual_questions_hr_table():

    cnxn = connection('PROMS_DEVELOPMENT')
    indquests_hr = pd.read_sql(ind_quest_HR(DATE_TO,DATE_FROM, YEAR_STRING,TABLE),cnxn)
    return indquests_hr

def individual_questions_kr_table_old():

    cnxn = connection('PROMS_DEVELOPMENT')
    indquests_kr = pd.read_sql(ind_quest_KR(DATE_TO_MIN1,DATE_FROM_MIN1,YEAR_STRING_MIN1,PREVIOUS_TABLE),cnxn)
    return indquests_kr

def individual_questions_hr_table_old():

    cnxn = connection('PROMS_DEVELOPMENT')
    indquests_hr = pd.read_sql(ind_quest_HR(DATE_TO_MIN1,DATE_FROM_MIN1,YEAR_STRING_MIN1,PREVIOUS_TABLE),cnxn)
    return indquests_hr
