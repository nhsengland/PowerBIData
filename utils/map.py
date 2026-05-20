def using_map_data():
    from utils.connection import connection
    from utils.queries import map
    from config import DATE_FROM, DATE_TO,YEAR_STRING,CURRENT_YEAR,TABLE
    import pandas as pd

    cnxn = connection('PROMS_PUBLICATION')
    maps = pd.read_sql(map(DATE_FROM,DATE_TO,CURRENT_YEAR,YEAR_STRING,TABLE),cnxn)
    return maps 

def map_previous_year():
    from utils.connection import connection
    from utils.queries import map
    from config import DATE_FROM_MIN1, DATE_TO_MIN1,YEAR_STRING_MIN1,PREVIOUS_YEAR,PREVIOUS_TABLE
    import pandas as pd

    cnxn = connection('PROMS_PUBLICATION')
    maps = pd.read_sql(map(DATE_FROM_MIN1,DATE_TO_MIN1,PREVIOUS_YEAR,YEAR_STRING_MIN1,PREVIOUS_TABLE),cnxn)
    return maps 