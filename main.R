library("duckdb")
library(connections)
library(dplyr)
options("duckdb.enable_rstudio_connection_pane" = TRUE) # fancier connection views, not on by default

# to start an in-memory database
con <- DBI::dbConnect(duckdb::duckdb(), 'data/catalog.ducklake', read_only=TRUE)

# if required
# DBI::dbExecute(con, "INSTALL ducklake")
# DBI::dbExecute(con, "ATTACH 'ducklake:data/catalog.ducklake'")
DBI::dbExecute(con, "USE catalog;")
connection_open(duckdb::duckdb(), 'data/catalog.ducklake')
con |> sql('SELECT * FROM catalog.raw.events')
tbl(con, I('raw.events'))
DBI::dbDisconnect(con)
DBI::dbDisconnect(con)
