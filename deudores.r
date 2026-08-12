library(tidyverse)
library(viewxl)
library(arrow)

#dir<-"C:/Users/SYC/Downloads/deudores"

#setwd(dir)
actividades<-read_parquet("data/actividades_clean.parquet") |> 
  rename(actividad=codigo_actividad)
entidades<-read_parquet("data/maeent_clean.parquet") |> 
  rename(entidad=codigo_entidad)
deudores<-read_parquet("data/deuda.parquet") |> 
  mutate(entidad=as.numeric(entidad)) |> 
  left_join(entidades,by="entidad") |> 
  select(nombre_entidad,situacion,provincia,everything()) |> 
  select(-entidad) |> 
  mutate(provincia=case_when(
    provincia==0~"CABA",
    provincia==1~"Buenos Aires",
    provincia==2~"Catamarca",
    provincia==3~"Córdoba",
    provincia==4~"Corrientes",
    provincia==5~"Entre Ríos",
    provincia==6~"Jujuy",
    provincia==7~"Mendoza",
    provincia==8~"La Rioja",
    provincia==9~"Salta",
    provincia==10~"San Juan",
    provincia==11~"San Luis",
    provincia==12~"Santa Fe",
    provincia==13~"Santiago del Estero",
    provincia==14~"Tucumán",
    provincia==16~"Chaco",
    provincia==17~"Chubut",
    provincia==18~"Formosa",
    provincia==19~"Misiones",
    provincia==20~"Neuquen",
    provincia==21~"La Pampa",
    provincia==22~"Río Negro",
    provincia==23~"Santa Cruz",
    provincia==24~"Tierra del Fuego"
  )) |> mutate(anio="2026",mes="6") |> 
    mutate(situacion_mora=ifelse(situacion %in% c("1","2"),"Situación normal o de bajo riesgo","En mora"))

write_parquet(deudores,'data/deuda_clean.parquet')




  

