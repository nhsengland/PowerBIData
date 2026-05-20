from utils.connection import connection
from utils.queries import annualreportahg,successatisf,complications_stats
from config import DATE_TO,TABLE,DATE_FROM,FYEAR,YEAR_STRING,PREVIOUS_TABLE,DATE_FROM_MIN1,DATE_TO_MIN1,PREVIOUS_FYEAR,YEAR_STRING_MIN1
import pandas as pd
from utils.formatting import add_percentage_symbol


def annual_report_ahg_table():
    '''produces the data by running the sql query for the annual report ahg for the current publication year'''
    cnxn = connection('PROMS_PUBLICATION')
    annual_reportahg_table = pd.read_sql(annualreportahg(TABLE,DATE_FROM,DATE_TO,FYEAR,YEAR_STRING),cnxn)
    return annual_reportahg_table

def annual_report_ahg_table_old():
    '''produces the data by running the sql query for the annual report ahg for the previous publication year'''
    cnxn = connection('PROMS_PUBLICATION')
    annual_reportahg_table = pd.read_sql(annualreportahg(PREVIOUS_TABLE,DATE_FROM_MIN1,DATE_TO_MIN1,PREVIOUS_FYEAR,YEAR_STRING_MIN1),cnxn)
    return annual_reportahg_table

def success_satisfaction():
    '''produces the data by running the sql query for the success satisfaction sheet for the current publication year'''
    cnxn = connection('PROMS_PUBLICATION')
    succ_satisfacation_data = pd.read_sql(successatisf(YEAR_STRING,TABLE,DATE_FROM,DATE_TO),cnxn)
    succ_satisfacation_data["Percentage"] = succ_satisfacation_data["Percentage"].round(decimals=1)
    succ_satisfacation_data["Percentage"] = add_percentage_symbol(succ_satisfacation_data["Percentage"])
    return succ_satisfacation_data

def success_satisfaction_old():
    '''produces the data by running the sql query for the success satisfaction sheet for the previous publication year'''
    cnxn = connection('PROMS_PUBLICATION')
    succ_satisfacation_data = pd.read_sql(successatisf(YEAR_STRING_MIN1,PREVIOUS_TABLE,DATE_FROM_MIN1,DATE_TO_MIN1),cnxn)
    succ_satisfacation_data["Percentage"] = succ_satisfacation_data["Percentage"].round(decimals=1)
    succ_satisfacation_data["Percentage"] = add_percentage_symbol(succ_satisfacation_data["Percentage"]    )
    return succ_satisfacation_data

def complications_table():
    '''produces the data for the complications sheet by running the sql query for the current publication year'''
    cnxn = connection('PROMS_PUBLICATION')
    complications_data = pd.read_sql(complications_stats(TABLE,DATE_FROM,DATE_TO,YEAR_STRING),cnxn)
    complications_data["Percentage"] = add_percentage_symbol(complications_data["Percentage"])
    return complications_data

def complications_table_old():
    '''produces the data for the complications sheet by running the sql query for the previous publication year'''
    cnxn = connection('PROMS_PUBLICATION')
    complications_data = pd.read_sql(complications_stats(PREVIOUS_TABLE,DATE_FROM_MIN1,DATE_TO_MIN1,YEAR_STRING_MIN1),cnxn)
    complications_data["Percentage"] = add_percentage_symbol(complications_data["Percentage"])
    return complications_data