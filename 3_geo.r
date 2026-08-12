library(tidyverse)
library(sf)
library(arrow)

pol <- st_read("data/linea_de_limite_070111/linea_de_limite_070111Line.shp") |> 
  mutate(nam=str_replace(nam,"Ciudad Autónoma de Buenos Aires","CABA"),
nam=str_replace(nam,"Tierra del Fuego, Antártida e Islas del Atlántico Sur","Tierra del Fuego"))

