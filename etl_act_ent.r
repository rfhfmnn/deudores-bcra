library(tidyverse)
library(data.table)
library(arrow)

dir<-"C:/Users/SYC/Downloads/deudores"
setwd(dir)

actividades <- read_fwf(
  file = "Actividades_ARCA.txt",
  col_positions = fwf_widths(
    widths = c(6, 254),
    col_names = c("actividad", "descripcion")
  ),
  col_types = cols(.default = "c"),
  locale = locale(encoding = "ISO-8859-1")  
)

actividades$actividad <- trimws(actividades$actividad)
actividades$descripcion <- trimws(actividades$descripcion)


entidades <- read_fwf(
  file = "Maeent.txt",
  col_positions = fwf_widths(
    widths = c(5, 70),
    col_names = c("entidad", "nombre_entidad")
  ),
  col_types = cols(.default = "c"),
  locale = locale(encoding = "ISO-8859-1")  
)

entidades$entidad <- trimws(entidades$entidad)
entidades$nombre_entidad <- trimws(entidades$nombre_entidad)

write_parquet(actividades, "deudores-bcra/data/actividades.parquet")
write_parquet(entidades, "deudores-bcra/data/entidades.parquet")

