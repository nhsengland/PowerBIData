import pyodbc


def connection(database):
    '''
    Creates the connection to the server and database, 
    given the database you want to connect to,
    returning the connection that can then be used to run an SQL query
    '''

    connection_string = f'''Driver={{SQL Server Native Client 11.0}};
                           Server=phh-l-prmsql-l1;
                           Database={database};
                           Trusted_Connection=yes;'''

    return pyodbc.connect(connection_string)
    