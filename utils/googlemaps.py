def google_maps_data():
    '''runs google maps query '''
    from utils.connection import connection
    from utils.queries import mapping
    from config import FYEAR,YEAR_STRING,TABLE
    import pandas as pd

    cnxn = connection('PROMS_PUBLICATION')
    keyfacts = pd.read_sql(mapping(FYEAR,YEAR_STRING,TABLE),cnxn)
    return keyfacts 
