import pandas as pd
import numpy as np

_DF = None

def cargar_dataframe():
    """Carga y limpia el Excel con la misma lógica de cargar_excel.py."""
    global _DF
    if _DF is not None:
        return _DF

    df = pd.read_excel("excels/trabajo_Practico.xlsx")
    
    # Limpieza básica
    if "FECHA" in df.columns:
        df = df.drop(columns=["FECHA"])
        
    if "ccodana" in df.columns and df["ccodana"].dtype == object:
        df["ccodana"] = df["ccodana"].astype(str).str.strip()
    if "HORA REUNIÓN" in df.columns and df["HORA REUNIÓN"].dtype == object:
        df["HORA REUNIÓN"] = df["HORA REUNIÓN"].astype(str).str.strip()

    # Estandarizar nombres de columnas a minúsculas con guiones bajos
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    renombrar = {
        "código_grupo": "codigo_grupo",
        "código_cuenta": "codigo_cuenta",
        "fecha_reunión": "fecha_reunion",
        "hora_reunión": "hora_reunion",
        "dirección": "direccion",
        "nombre_grupo_/_clienta_ccm": "nombre_unidad",
        "categoria_asesor": "categoria_asesor",
        "cuotas_aprob": "cuotas_aprobadas",
        "nro_cuotas_atrasadas": "nro_cuotas_atrasadas",
        "nro_cuota_actual": "nro_cuota_actual",
        "mto_cuota": "mto_cuota",
        "saldo_capital": "saldo_capital",
        "fecha_desembolso": "fecha_desembolso"
    }
    df = df.rename(columns=renombrar)

    # Nulos en cuotas atrasadas a 0
    if "nro_cuotas_atrasadas" in df.columns:
        df["nro_cuotas_atrasadas"] = pd.to_numeric(df["nro_cuotas_atrasadas"], errors="coerce").fillna(0)

    # Fechas
    if "fecha_desembolso" in df.columns:
        df["fecha_desembolso"] = pd.to_datetime(df["fecha_desembolso"], errors="coerce")

    # Crear una columna id única
    if "id" not in df.columns:
        df.insert(0, "id", range(1, len(df) + 1))

    _DF = df
    return _DF


def listar(tabla=None, limite=500):
    df = cargar_dataframe()
    sub_df = df.head(limite).fillna("")
    return sub_df.to_dict("records")


def agregar(tabla, fila):
    global _DF
    df = cargar_dataframe()
    nuevo_id = int(df["id"].max() + 1) if not df.empty else 1
    fila["id"] = nuevo_id
    nueva_fila_df = pd.DataFrame([fila])
    _DF = pd.concat([df, nueva_fila_df], ignore_index=True)


def editar(tabla, id_, fila):
    global _DF
    df = cargar_dataframe()
    idx = df[df["id"] == id_].index
    if not idx.empty:
        for col, val in fila.items():
            if col in df.columns:
                _DF.loc[idx[0], col] = val


def eliminar(tabla, id_):
    global _DF
    df = cargar_dataframe()
    _DF = df[df["id"] != id_].reset_index(drop=True)


def estadisticas():
    """Genera las métricas y datos de gráficos rescatando los análisis clave."""
    df = cargar_dataframe()

    total_creditos = len(df)
    total_desembolso = float(pd.to_numeric(df["desembolso"], errors="coerce").sum())
    prom_desembolso = float(pd.to_numeric(df["desembolso"], errors="coerce").mean())
    total_grupos = int(df["codigo_grupo"].nunique()) if "codigo_grupo" in df.columns else total_creditos

    df_temp = df.copy()
    df_temp["desembolso_num"] = pd.to_numeric(df_temp["desembolso"], errors="coerce").fillna(0)

    # 1. Top 10 Distritos por promedio de desembolso
    prom_distrito = (
        df_temp.groupby("distrito")["desembolso_num"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
        .head(10)
    )

    # 2. Total Desembolso por Oficina (Suma, ordenado desc)
    desembolso_oficina = (
        df_temp.groupby("oficina")["desembolso_num"]
        .sum()
        .round(2)
        .sort_values(ascending=False)
    )

    # 3. Cantidad de Grupos Únicos por Oficina
    grupos_oficina = (
        df.groupby("oficina")["codigo_grupo"]
        .nunique()
        .sort_values(ascending=False)
    )

    # 4. Top Oficinas con Mayor Cuotas Atrasadas
    df_temp["cuotas_atrasadas_num"] = pd.to_numeric(df_temp["nro_cuotas_atrasadas"], errors="coerce").fillna(0)
    atrasos_oficina = (
        df_temp.groupby("oficina")["cuotas_atrasadas_num"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    # 5. Evolución de los Desembolsos por Mes y Punto Óptimo
    df_fechas = df.dropna(subset=["fecha_desembolso"]).copy()
    df_fechas["mes"] = df_fechas["fecha_desembolso"].dt.to_period("M").astype(str)
    desembolso_mes = (
        df_fechas.groupby("mes")["desembolso"]
        .sum()
        .round(2)
        .sort_index()
    )
    mes_optimo = str(desembolso_mes.idxmax()) if not desembolso_mes.empty else ""
    valor_optimo = float(desembolso_mes.max()) if not desembolso_mes.empty else 0.0

    # 6. NUEVO: Top 5 Asesores con Mayor Desembolso Colocado
    top_asesores = (
        df_temp.groupby("asesor")["desembolso_num"]
        .sum()
        .round(2)
        .sort_values(ascending=False)
        .head(5)
    )

    # 7. NUEVO: Distribución por Categoría de Asesor (Junior, Master, etc.)
    categorias_asesor = df["categoria_asesor"].value_counts()

    # 8. NUEVO: Dinero Real Atrasado por Agencia (Mora Real en Soles)
    df_temp["mto_cuota_num"] = pd.to_numeric(df_temp["mto_cuota"], errors="coerce").fillna(0)
    df_temp["dinero_real_atrasado"] = df_temp["cuotas_atrasadas_num"] * df_temp["mto_cuota_num"]
    mora_real_oficina = (
        df_temp.groupby("oficina")["dinero_real_atrasado"]
        .sum()
        .round(2)
        .sort_values(ascending=False)
    )

    # 9. NUEVO: Ganancia Proyectada Esperada por Agencia
    df_temp["cuotas_aprobadas_num"] = pd.to_numeric(df_temp["cuotas_aprobadas"], errors="coerce").fillna(0)
    df_temp["ganancia_esperada"] = (df_temp["mto_cuota_num"] * df_temp["cuotas_aprobadas_num"]) - df_temp["desembolso_num"]
    ganancia_oficina = (
        df_temp.groupby("oficina")["ganancia_esperada"]
        .sum()
        .round(2)
        .sort_values(ascending=False)
    )

    # 10. NUEVO: Índice de Mora (%) por Oficina
    df_temp["saldo_capital_num"] = pd.to_numeric(df_temp["saldo_capital"], errors="coerce").fillna(0)
    df_eficiencia = df_temp.groupby("oficina").agg(
        saldo_capital_total=("saldo_capital_num", "sum"),
        dinero_atrasado_total=("dinero_real_atrasado", "sum")
    ).reset_index()
    df_eficiencia["porcentaje_mora"] = (
        df_eficiencia["dinero_atrasado_total"] / df_eficiencia["saldo_capital_total"].replace(0, float("inf"))
    ) * 100
    df_eficiencia = df_eficiencia.sort_values(by="porcentaje_mora", ascending=False)

    return {
        "totales": {
            "creditos": total_creditos,
            "total_desembolso": total_desembolso,
            "prom_desembolso": prom_desembolso,
            "grupos": total_grupos
        },
        "distritos": {
            "labels": prom_distrito.index.astype(str).tolist(),
            "valores": prom_distrito.values.tolist()
        },
        "desembolso_oficina": {
            "labels": desembolso_oficina.index.astype(str).tolist(),
            "valores": desembolso_oficina.values.tolist()
        },
        "grupos_oficina": {
            "labels": grupos_oficina.index.astype(str).tolist(),
            "valores": grupos_oficina.values.tolist()
        },
        "atrasos_oficina": {
            "labels": atrasos_oficina.index.astype(str).tolist(),
            "valores": atrasos_oficina.values.tolist()
        },
        "desembolso_mes": {
            "labels": desembolso_mes.index.astype(str).tolist(),
            "valores": desembolso_mes.values.tolist(),
            "mes_optimo": mes_optimo,
            "valor_optimo": valor_optimo
        },
        "top_asesores": {
            "labels": top_asesores.index.astype(str).tolist(),
            "valores": top_asesores.values.tolist()
        },
        "categorias_asesor": {
            "labels": categorias_asesor.index.astype(str).tolist(),
            "valores": categorias_asesor.values.tolist()
        },
        "mora_real_oficina": {
            "labels": mora_real_oficina.index.astype(str).tolist(),
            "valores": mora_real_oficina.values.tolist()
        },
        "ganancia_oficina": {
            "labels": ganancia_oficina.index.astype(str).tolist(),
            "valores": ganancia_oficina.values.tolist()
        },
        "indice_mora": {
            "labels": df_eficiencia["oficina"].astype(str).tolist(),
            "valores": df_eficiencia["porcentaje_mora"].round(2).tolist()
        }
    }


def ultimos_creditos(n=10):
    """Retorna los n créditos más recientes o de muestra."""
    df = cargar_dataframe()
    cols = ["id", "codigo_cuenta", "nombre_unidad", "oficina", "distrito", "desembolso", "mto_cuota", "nro_cuotas_atrasadas", "asesor"]
    cols_existentes = [c for c in cols if c in df.columns]
    return df[cols_existentes].head(n).fillna("").to_dict("records")
