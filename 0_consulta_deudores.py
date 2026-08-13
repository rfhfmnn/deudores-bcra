import duckdb
import polars as pl
import pandas as pd

con = duckdb.connect()

#deudores
con.sql("""
        COPY (
            WITH lineas AS (
                SELECT 
                    line,
                -- Separa los campos restantes a partir del carácter 30 por espacios
                    string_split_regex(trim(substr(line, 30)), '\s+') AS cols
                FROM read_csv('C:/Users/rafah/Documents/Deudores BCRA/deudores.txt', header=False, columns={'line': 'VARCHAR'})
            )
            SELECT 
            -- 1. Encabezado de Ancho Fijo (Primeros 29 caracteres)
                substr(line, 1, 5)                       AS entidad,
                substr(line, 6, 6)                       AS periodo,
                substr(line, 12, 2)                      AS tipo_doc,
                substr(line, 14, 11)                     AS cuit,
                TRY_CAST(substr(line, 25, 3) AS INT)     AS actividad,
                TRY_CAST(substr(line, 28, 2) AS INT)     AS situacion,

            -- 2. Montos e Indicadores (Campos 7 al 24)
                TRY_CAST(REPLACE(cols[1], ',', '.') AS DOUBLE)  AS prestamos_total_garantias,
                TRY_CAST(REPLACE(cols[2], ',', '.') AS DOUBLE)  AS sin_uso,
                TRY_CAST(REPLACE(cols[3], ',', '.') AS DOUBLE)  AS garantias_otorgadas,
                TRY_CAST(REPLACE(cols[4], ',', '.') AS DOUBLE)  AS otros_conceptos,
                TRY_CAST(REPLACE(cols[5], ',', '.') AS DOUBLE)  AS garantias_preferidas_a,
                TRY_CAST(REPLACE(cols[6], ',', '.') AS DOUBLE)  AS garantias_preferidas_b,
                TRY_CAST(REPLACE(cols[7], ',', '.') AS DOUBLE)  AS sin_garantias_preferidas,
                TRY_CAST(REPLACE(cols[8], ',', '.') AS DOUBLE)  AS contragarantias_preferidas_a,
                TRY_CAST(REPLACE(cols[9], ',', '.') AS DOUBLE)  AS contragarantias_preferidas_b,
                TRY_CAST(REPLACE(cols[10], ',', '.') AS DOUBLE) AS sin_contragarantias_preferidas,
                TRY_CAST(REPLACE(cols[11], ',', '.') AS DOUBLE) AS previsiones,
                TRY_CAST(cols[12] AS INT)                       AS deuda_cubierta,
                TRY_CAST(cols[13] AS INT)                       AS proceso_judicial_revision,
                TRY_CAST(cols[14] AS INT)                       AS refinanciaciones,
                TRY_CAST(cols[15] AS INT)                       AS recategorizacion_obligatoria,
                TRY_CAST(cols[16] AS INT)                       AS situacion_juridica,
                TRY_CAST(cols[17] AS INT)                       AS irrecuperables_tecnica,
                TRY_CAST(cols[18] AS INT)                       AS dias_atraso
            FROM lineas
        ) TO 'C:/Users/rafah/Documents/Deudores BCRA/deudores_clean.parquet' (FORMAT PARQUET)
    """)

#padron
con.sql("""
        COPY (
            WITH lineas AS (
                SELECT line
                FROM read_csv(
                    'C:/Users/rafah/Documents/Deudores BCRA/Padron_ARCA.txt', 
                    header=False, 
                    columns={'line': 'VARCHAR'},
                    quote='',
                    escape='',
                    encoding='CP1252',
                    ignore_errors=true,
                    auto_detect=False
                )
            )
            SELECT 
                -- 1. Identificación
                trim(substr(line, 1, 11))                           AS cuit,
                trim(substr(line, 12, 160))                         AS denominacion,
                TRY_CAST(trim(substr(line, 172, 6)) AS INT)         AS actividad,
            
            -- 2. Estado y Reemplazo
                NULLIF(trim(substr(line, 178, 1)), '')              AS marca_baja,
                NULLIF(trim(substr(line, 179, 11)), '')             AS cuit_reemplazo,
            
                -- 3. Fechas y Demografía
                TRY_CAST(
                    NULLIF(trim(substr(line, 190, 10)), '1901-01-01') 
                    AS DATE
                )                                                   AS fecha_nac_contrato,
            
                NULLIF(trim(substr(line, 200, 1)), '')              AS sexo,
                NULLIF(trim(substr(line, 201, 10)), '')             AS codigo_postal,
                TRY_CAST(trim(substr(line, 211, 2)) AS INT)         AS provincia,
            
                TRY_STRPTIME(
                    NULLIF(trim(substr(line, 213, 8)), '19010101'), 
                    '%Y%m%d'
                )::DATE                                             AS fecha_fallecimiento

            FROM lineas
        ) TO 'C:/Users/rafah/Documents/Deudores BCRA/padron_arca_clean.parquet' (FORMAT PARQUET, COMPRESSION 'ZSTD')
    """)

#esquemas
schema = duckdb.sql("DESCRIBE SELECT * FROM 'C:/Users/rafah/Documents/Deudores BCRA/deudores_clean.parquet'").df()
print(schema)

schema_padron = duckdb.sql("DESCRIBE SELECT * FROM 'C:/Users/rafah/Documents/Deudores BCRA/padron_arca_clean.parquet'").df()
print(schema_padron)

#etl
con.sql("""
        COPY (
            WITH base AS (
                SELECT 
                    d.periodo,
                    d.entidad,
                    d.situacion,
                    p.provincia,
                    p.sexo,
                    d.cuit,
                    CASE 
                        WHEN CAST(d.cuit AS VARCHAR) LIKE '3%' THEN 'Jurídica'
                        WHEN CAST(d.cuit AS VARCHAR) LIKE '2%' THEN 'Física'
                        ELSE 'Otra/Desconocida'
                    END AS tipo_persona,
                    CASE 
                        WHEN CAST(d.cuit AS VARCHAR) LIKE '3%' THEN CAST(p.actividad AS VARCHAR)
                        ELSE 'N/A' 
                    END AS actividad,
                    d.prestamos_total_garantias
                FROM 
                    'C:/Users/SYC/Downloads/deudores/deudores_clean.parquet' d
                LEFT JOIN 
                    'C:/Users/SYC/Downloads/deudores/padron_arca_clean.parquet' p 
                    ON d.cuit = p.cuit
            )
            SELECT 
                entidad,
                periodo,
                situacion,
                provincia,
                sexo,
                tipo_persona,
                actividad,
                SUM(prestamos_total_garantias) AS prestamos,
                COUNT(DISTINCT cuit) AS cantidad_deudores
            FROM base
            GROUP BY 
                entidad,
                periodo,
                situacion,
                provincia,
                sexo,
                tipo_persona,
                actividad
        ) TO 'data/deuda_new.parquet' (FORMAT PARQUET)
    """)
