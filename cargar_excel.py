import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# 1. CARGA DEL ARCHIVO EXCEL
df = pd.read_excel("excels/trabajo_Practico.xlsx")
print("Dimensiones iniciales:", df.shape)
print("-" * 80)
# 2. AUDITORÍA INICIAL
print("Primeras 3 filas:")
print(df.head(3))
print("-" * 80)
print("Valores nulos por columna:")
print(df.isna().sum())
print("-" * 80)
print("Registros duplicados:", df.duplicated().sum())
print("-" * 80)
# 3. LIMPIEZA DE DATOS
# A. Eliminar columna FECHA vacía
if "FECHA" in df.columns:
    df = df.drop(columns=["FECHA"])
# B. Limpieza de espacios residuales en texto
if "ccodana" in df.columns:
    df["ccodana"] = df["ccodana"].astype(str).str.strip()
if "HORA REUNIÓN" in df.columns:
    df["HORA REUNIÓN"] = df["HORA REUNIÓN"].astype(str).str.strip()
# C. Normalizar columnas a minúsculas y reemplazar espacios
df.columns = df.columns.str.lower().str.replace(" ", "_")
# D. Renombrar columnas con tildes o caracteres especiales
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
# E. Rellenar nulos en cuotas atrasadas con 0 (al día)
df["nro_cuotas_atrasadas"] = pd.to_numeric(df["nro_cuotas_atrasadas"], errors="coerce").fillna(0)
# F. Convertir fecha de desembolso a datetime y numéricos
df["fecha_desembolso"] = pd.to_datetime(df["fecha_desembolso"], errors="coerce")
df["desembolso_num"] = pd.to_numeric(df["desembolso"], errors="coerce").fillna(0)
df["mto_cuota_num"] = pd.to_numeric(df["mto_cuota"], errors="coerce").fillna(0)
df["cuotas_aprobadas_num"] = pd.to_numeric(df["cuotas_aprobadas"], errors="coerce").fillna(0)
print("Columnas limpias y listas:")
print(df.columns.tolist())
print("-" * 80)
# 4. ANÁLISIS ESTADÍSTICO GENERAL
print(f"Total Desembolsado: S/. {df['desembolso_num'].sum():,.2f}")
print(f"Promedio de Desembolso: S/. {df['desembolso_num'].mean():,.2f}")
print(f"Total Grupos Únicos: {df['codigo_grupo'].nunique()}")
print("-" * 80)
# ==============================================================================
# 5. VISUALIZACIONES CON MATPLOTLIB (Los 10 análisis del proyecto)
# ==============================================================================
# GRÁFICA 1: Evolución de los Desembolsos por Mes
df_fechas = df.dropna(subset=["fecha_desembolso"]).copy()
df_fechas["mes"] = df_fechas["fecha_desembolso"].dt.to_period("M").astype(str)
desembolso_mes = df_fechas.groupby("mes")["desembolso_num"].sum()
plt.figure(figsize=(10, 5))
plt.plot(desembolso_mes.index, desembolso_mes.values / 1e6, marker="o", color="#0d6efd", linewidth=2)
plt.title("1. Evolución de los Desembolsos por Mes (Compartamos)", fontsize=13, fontweight="bold")
plt.xlabel("Mes")
plt.ylabel("Millones de Soles (S/. M)")
plt.xticks(rotation=45)
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()
# GRÁFICA 2: Desembolso Total por Agencia (Barras Horizontales)
desembolso_oficina = df.groupby("oficina")["desembolso_num"].sum().sort_values(ascending=True)
plt.figure(figsize=(9, 5))
plt.barh(desembolso_oficina.index, desembolso_oficina.values / 1e6, color="#198754")
plt.title("2. Desembolso Total Acumulado por Agencia", fontsize=13, fontweight="bold")
plt.xlabel("Millones de Soles (S/. M)")
plt.ylabel("Agencia / Oficina")
plt.grid(axis="x", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()
# GRÁFICA 3: Top 5 Asesores con Mayor Colocación
top_asesores = df.groupby("asesor")["desembolso_num"].sum().sort_values(ascending=True).tail(5)
plt.figure(figsize=(10, 5))
plt.barh(top_asesores.index, top_asesores.values / 1e6, color="#ffc107", edgecolor="#d39e00")
plt.title("3. Top 5 Asesores con Mayor Monto Colocado", fontsize=13, fontweight="bold")
plt.xlabel("Monto Colocado (S/. M)")
plt.tight_layout()
plt.show()
# GRÁFICA 4: Distribución por Categoría de Asesor (Pie / Torta)
categorias = df["categoria_asesor"].value_counts()
plt.figure(figsize=(7, 7))
plt.pie(categorias.values, labels=categorias.index, autopct="%1.1f%%", colors=["#6f42c1", "#0dcaf0", "#20c997", "#fd7e14"], startangle=140)
plt.title("4. Distribución de Operaciones por Categoría de Asesor", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.show()
# GRÁFICA 5: Top 10 Distritos por Promedio de Desembolso
prom_distrito = df.groupby("distrito")["desembolso_num"].mean().sort_values(ascending=False).head(10)
plt.figure(figsize=(11, 5))
plt.bar(prom_distrito.index, prom_distrito.values, color="#0dcaf0", edgecolor="#0aa2c0")
plt.title("5. Top 10 Distritos por Promedio de Desembolso", fontsize=13, fontweight="bold")
plt.xlabel("Distrito")
plt.ylabel("Promedio Desembolso (S/.)")
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()
# GRÁFICA 6: Cantidad de Grupos Únicos por Agencia
grupos_oficina = df.groupby("oficina")["codigo_grupo"].nunique().sort_values(ascending=False)
plt.figure(figsize=(9, 5))
plt.bar(grupos_oficina.index, grupos_oficina.values, color="#20c997", edgecolor="#13795b")
plt.title("6. Cantidad de Grupos Únicos por Agencia", fontsize=13, fontweight="bold")
plt.xlabel("Agencia")
plt.ylabel("N° Grupos Solidarios")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()
# GRÁFICA 7: Cuotas Atrasadas por Agencia (Riesgo / Mora en cantidad de cuotas)
atrasos_oficina = df.groupby("oficina")["nro_cuotas_atrasadas"].sum().sort_values(ascending=False)
plt.figure(figsize=(9, 5))
plt.bar(atrasos_oficina.index, atrasos_oficina.values, color="#dc3545", edgecolor="#a71d2a")
plt.title("7. Cuotas Atrasadas por Agencia (Mora)", fontsize=13, fontweight="bold")
plt.xlabel("Agencia")
plt.ylabel("Total Cuotas Impagas")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()
# GRÁFICA 8: Punto Óptimo de Ganancias / Desembolsos
mes_optimo = desembolso_mes.idxmax()
valor_optimo = desembolso_mes.max()
plt.figure(figsize=(10, 5))
plt.plot(desembolso_mes.index, desembolso_mes.values / 1e6, marker="o", color="#890dfd", linewidth=2)
plt.scatter(mes_optimo, valor_optimo / 1e6, color="red", edgecolor="black", s=110, zorder=5)
plt.annotate(
    f"Punto Óptimo: S/. {valor_optimo / 1e6:.2f}M",
    xy=(mes_optimo, valor_optimo / 1e6),
    xytext=(5.3, (valor_optimo / 1e6) - 2),
    arrowprops=dict(facecolor="black", shrink=0.08, width=1.5, headwidth=7),
    ha="center",
    fontweight="bold"
)
plt.ylim(top=30)
plt.axhline(valor_optimo / 1e6, color="red", linestyle="--", alpha=0.5)
plt.title("8. Evolución de Desembolsos y Punto Óptimo (Pico Máximo)", fontsize=13, fontweight="bold")
plt.xlabel("Mes")
plt.ylabel("Millones de Soles (S/. M)")
plt.xticks(rotation=45)
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()
# GRÁFICA 9: Dinero Real Atrasado por Agencia (Mora en Soles)
df["dinero_real_atrasado"] = df["nro_cuotas_atrasadas"] * df["mto_cuota_num"]
mora_oficina = df.groupby("oficina")["dinero_real_atrasado"].sum().sort_values(ascending=False)
print("--- Dinero Real Atrasado por Agencia ---")
print(mora_oficina.apply(lambda x: f"S/. {x:,.2f}"))
print("-" * 80)
plt.figure(figsize=(10, 5))
plt.bar(mora_oficina.index, mora_oficina.values / 1e3, color="crimson", edgecolor="darkred")
plt.title("9. Dinero Real Atrasado por Agencia (Monto Cuota × Cuotas Atrasadas)", fontsize=13, fontweight="bold")
plt.xlabel("Agencia / Oficina")
plt.ylabel("Miles de Soles (S/. K)")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.6)
ax = plt.gca()
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"S/. {x:,.0f}K"))
plt.tight_layout()
plt.show()
# GRÁFICA 10: Ganancia Proyectada Esperada por Agencia
df["ganancia_esperada"] = (df["mto_cuota_num"] * df["cuotas_aprobadas_num"]) - df["desembolso_num"]
ganancia_oficina = df.groupby("oficina")["ganancia_esperada"].sum().sort_values(ascending=False)
print("--- Ganancia Esperada Proyectada por Agencia ---")
print(ganancia_oficina.apply(lambda x: f"S/. {x:,.2f}"))
print("-" * 80)
plt.figure(figsize=(10, 5))
plt.bar(ganancia_oficina.index, ganancia_oficina.values / 1e6, color="forestgreen", edgecolor="darkgreen")
plt.title("10. Ganancia Proyectada Esperada por Agencia\n((Monto Cuota × Cuotas Aprobadas) - Desembolso)", fontsize=13, fontweight="bold")
plt.xlabel("Agencia / Oficina")
plt.ylabel("Millones de Soles (S/. M)")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.6)
ax = plt.gca()
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"S/. {x:,.1f}M"))
plt.tight_layout()
plt.show()
# ==============================================================================
# GRÁFICA 11: Índice de Mora (%) por Oficina
# ==============================================================================
df["saldo_capital_num"] = pd.to_numeric(df["saldo_capital"], errors="coerce").fillna(0)
df_eficiencia = df.groupby("oficina").agg(
    saldo_capital_total=("saldo_capital_num", "sum"),
    dinero_atrasado_total=("dinero_real_atrasado", "sum")
).reset_index()
df_eficiencia["porcentaje_mora"] = (
    df_eficiencia["dinero_atrasado_total"] / df_eficiencia["saldo_capital_total"].replace(0, float("inf"))
) * 100
df_eficiencia = df_eficiencia.sort_values(by="porcentaje_mora", ascending=False)
print("--- Índice de Mora (%) por Oficina ---")
for _, r in df_eficiencia.iterrows():
    print(f"{r['oficina']}: {r['porcentaje_mora']:.2f}% (Mora: S/. {r['dinero_atrasado_total']:,.2f} / Cartera: S/. {r['saldo_capital_total']:,.2f})")
print("-" * 80)
plt.figure(figsize=(10, 5))
plt.bar(df_eficiencia["oficina"], df_eficiencia["porcentaje_mora"], color="darkorange", edgecolor="#c25e00")
plt.title("11. Índice de Mora (%) por Oficina\n((Dinero Atrasado / Saldo Capital Total) × 100)", fontsize=13, fontweight="bold")
plt.xlabel("Agencia / Oficina")
plt.ylabel("Porcentaje de Mora (%)")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.6)
ax = plt.gca()
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{x:.1f}%"))
plt.tight_layout()
plt.show()