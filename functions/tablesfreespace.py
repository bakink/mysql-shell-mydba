import __builtin__
from mysqlsh import globals

# see https://lefred.be/content/overview-of-fragmented-mysql-innodb-tables/

def getFragmentedTables(percentage=10):
    # Get the session and ensure it is connected
    if not globals.session.is_open():
        print("Please create a connection first.")
        return False
    session=globals.session
    stmt = "select variable_value from performance_schema.global_variables where variable_name='information_schema_stats_expiry';"
    query = session.sql(stmt)
    result = query.execute()
    stats = result.fetch_all()
    if len(stats) > 0:
       for stat in stats:
           if stat > 0:
               print "Warning: information_schema_stats_expiry is set to {0}.".format(*stat)


    stmt = """SELECT CONCAT(table_schema, '.', table_name) as 'TABLE', 
       ENGINE, CONCAT(ROUND(table_rows / 1000000, 2), 'M') `ROWS`, 
       CONCAT(ROUND(data_length / ( 1024 * 1024 * 1024 ), 2), 'G') DATA, 
       CONCAT(ROUND(index_length / ( 1024 * 1024 * 1024 ), 2), 'G') IDX, 
       CONCAT(ROUND(( data_length + index_length ) / ( 1024 * 1024 * 1024 ), 2), 'G') 'TOTAL SIZE', 
       ROUND(index_length / data_length, 2)  IDXFRAC, 
        CONCAT(ROUND(( data_free / 1024 / 1024),2), 'MB') AS data_free,
       CONCAT('(',
        IF(data_free< ( data_length + index_length ), 
        CONCAT(round(data_free/(data_length+index_length)*100,2),'%'),
       '100%'),')') AS data_free_pct
       FROM information_schema.TABLES  WHERE (data_free/(data_length+index_length)*100) > {limit}
       AND table_schema <> 'mysql';""".format(limit=percentage) 
    query = session.sql(stmt)
    result = query.execute()
    tables = result.fetch_all()
    fmt_h = "| {0:30} | {1:10} | {2:7} | {3:10} | {4:10} | {5:10} | {6:17} |"
    fmt = "| {0:30} | {1:10} | {2:>7} | {3:>10} | {4:>10} | {5:>10} | {7:>7} {8:8} |"
    header = fmt_h.format("Table","Engine","# Rows", "Data Size", "Idx Size", "Total Size", "Data Free")
    bar = "+" + "-" * 32 + "+" + "-" * 12 + "+" + "-" * 9 + "+" + "-" * 12 + \
          "+" + "-" * 12 + "+" + "-" * 12 + "+" + "-" * 19 + "+"
    if len(tables) > 0:
        print bar
        print header
        print bar
    for table in tables:
        sql = fmt.format(*table)
        print(sql)
    if len(tables) > 0:
        print bar
 

