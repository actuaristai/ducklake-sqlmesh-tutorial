import duckdb
import ibis


ibis.options.interactive = True

# use this code snippet to show the connection pane on the right. note need to close connection to reduce conflicts.
connection_pane = duckdb.connect()
connection_pane.install_extension("ducklake")
connection_pane.sql("ATTACH 'ducklake:data/catalog.ducklake' AS my_lakehouse")
%connection_show connection_pane
connection_pane.close()


def main():
    print("Showing example of how to use with ibis")
    con = ibis.duckdb.connect(extensions="ducklake")
    con.attach(path="ducklake:data/catalog.ducklake", name='my_lakehouse')
    events = con.table('events', database='my_lakehouse.raw')
    stg_events = con.table('stg_events', database='my_lakehouse.staging')
    daily_revenue = con.table(
        'daily_revenue', database='my_lakehouse.analytics')
    con.list_tables(database='my_lakehouse.raw')
    con.list_tables(database='my_lakehouse.staging')
    con.list_tables(database='my_lakehouse.analytics')
    con.list_databases(catalog='my_lakehouse')
    con.list_catalogs()
    con.disconnect()


if __name__ == "__main__":
    main()
