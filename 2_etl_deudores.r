library(tidyverse)
library(arrow)
library(lubridate)

path_new <- "data/deuda_new.parquet"           
path_old <- "data/deuda_old.parquet"    

actividades <- read_parquet("data/actividades.parquet")
entidades   <- read_parquet("data/entidades.parquet")

deudores_new <- read_parquet(path_new) |> 
  mutate(periodo = ym(periodo)) |> 
  left_join(entidades, by = "entidad") |> 
  select(periodo, nombre_entidad, situacion, provincia, everything()) |> 
  mutate(provincia = case_when(
    provincia == 0  ~ "CABA",
    provincia == 1  ~ "Buenos Aires",
    provincia == 2  ~ "Catamarca",
    provincia == 3  ~ "Córdoba",
    provincia == 4  ~ "Corrientes",
    provincia == 5  ~ "Entre Ríos",
    provincia == 6  ~ "Jujuy",
    provincia == 7  ~ "Mendoza",
    provincia == 8  ~ "La Rioja",
    provincia == 9  ~ "Salta",
    provincia == 10 ~ "San Juan",
    provincia == 11 ~ "San Luis",
    provincia == 12 ~ "Santa Fe",
    provincia == 13 ~ "Santiago del Estero",
    provincia == 14 ~ "Tucumán",
    provincia == 16 ~ "Chaco",
    provincia == 17 ~ "Chubut",
    provincia == 18 ~ "Formosa",
    provincia == 19 ~ "Misiones",
    provincia == 20 ~ "Neuquén",
    provincia == 21 ~ "La Pampa",
    provincia == 22 ~ "Río Negro",
    provincia == 23 ~ "Santa Cruz",
    provincia == 24 ~ "Tierra del Fuego",
    TRUE            ~ "Sin Identificar"
  )) |> 
  mutate(situacion_mora = ifelse(situacion %in% c(1, 2), "Normal/Bajo riesgo", "En mora")) |> 
  replace_na(list(sexo = "Empresa")) |> 
  left_join(actividades, by = "actividad") |> 
  replace_na(list(descripcion = "Sin actividad")) |> 
  select(-actividad)


if (file.exists(path_old)) {
  message("cargando historico existente")
  deudores_old <- read_parquet(path_old)
  
  deudores_old_filtrado <- deudores_old |> 
    anti_join(deudores_new, by = c("entidad", "periodo"))
  
  deudores_acumulado <- bind_rows(deudores_old_filtrado, deudores_new)
  
} else {
  message("no hay histórica, creando base de cero")
  deudores_acumulado <- deudores_new
}

write_parquet(deudores_acumulado, path_old)
message("histórica actualizada")

