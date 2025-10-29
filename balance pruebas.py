import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import BytesIO
import xlsxwriter
from functools import reduce
from streamlit_option_menu import option_menu


st.set_page_config(
    page_title="Balance general",
    page_icon="🚚", 
    layout="wide"
)

logo_base64 = """
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
"""
st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="data:image/png;base64,{logo_base64}" alt="Logo de la Empresa" width="300">
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("BALANCE GENERAL")

# --- BOTÓN PARA RECARGAR INFORMACIÓN ---
st.markdown("### 🔄 Actualizar información")

if st.button("♻️ Recargar datos"):
    st.cache_data.clear()

# --- Cargar datos --- /secrets de streamlit
balance_url = st.secrets["urls"]["balance_url"]
mapeo_url = st.secrets["urls"]["mapeo_url"]
info_manual = st.secrets["urls"]["info_manual"]

hojas_empresas = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]

@st.cache_data(show_spinner="🧩 Cargando mapeo de cuentas...")
def cargar_mapeo(url: str) -> pd.DataFrame:
    """Descarga y carga el archivo de mapeo de cuentas."""
    r = requests.get(url)
    r.raise_for_status()
    file = BytesIO(r.content)
    df_mapeo = pd.read_excel(file, sheet_name=None, engine="openpyxl")

    if isinstance(df_mapeo, dict):
        df_mapeo = list(df_mapeo.values())[0]  # Si el Excel tiene varias hojas, tomar la primera

    df_mapeo.columns = df_mapeo.columns.str.strip()
    return df_mapeo
@st.cache_data(show_spinner="📘 Cargando hojas del balance...")
def cargar_hojas(url: str, hojas: list) -> dict:
    """Descarga y carga las hojas específicas del archivo de balance."""
    r = requests.get(url)
    r.raise_for_status()
    file = BytesIO(r.content)
    data = {}

    for hoja in hojas:
        try:
            df = pd.read_excel(file, sheet_name=hoja, engine="openpyxl")
            df.columns = df.columns.str.strip()
            data[hoja] = df
        except Exception as e:
            st.warning(f"⚠️ No se pudo leer la hoja {hoja}: {e}")

    return data
@st.cache_data(show_spinner="📋 Cargando información manual (Interempresas)...")
def cargar_info_manual(url: str) -> pd.DataFrame:
    """Carga la hoja INTEREMPRESAS del archivo Info Manual."""
    r = requests.get(url)
    r.raise_for_status()
    file = BytesIO(r.content)
    df_info = pd.read_excel(file, sheet_name="INTEREMPRESAS", engine="openpyxl")
    df_info.columns = df_info.columns.str.strip()
    return df_info

df_mapeo = cargar_mapeo(mapeo_url)         # ✅ Aquí ya se define df_mapeo
data_hojas = cargar_hojas(balance_url, hojas_empresas)
df_info_manual = cargar_info_manual(info_manual)

posibles_columnas_cuenta = ["CUENTA", "Descripción"]
col_cuenta_mapeo = next((c for c in posibles_columnas_cuenta if c in df_mapeo.columns), None)

posibles_columnas_monto = ["Saldo Final", "Saldo final"]
col_monto = next((c for c in posibles_columnas_monto if c in df_mapeo.columns), None) or "Saldo Final"
resultados = []
totales_globales = {}

OPTIONS = [
    "BALANCE POR EMPRESA",
    "BALANCE GENERAL ACUMULADO",
    "BALANCE FINAL",
]

selected = option_menu(
    menu_title=None,
    options=OPTIONS,
    icons=["building", "bar-chart-line", "clipboard-data"],
    default_index=0,
    orientation="horizontal"
)


def tabla_balance_por_empresa():
    st.subheader("📊 Balance General por Empresa")

    # Usa las variables globales cargadas previamente
    global df_mapeo, data_hojas

    # --- Columnas detectadas ---
    posibles_columnas_cuenta = ["Cuenta", "Descripción"]
    col_cuenta_mapeo = next((c for c in posibles_columnas_cuenta if c in df_mapeo.columns), None)
    posibles_columnas_monto = ["Saldo Final", "Saldo final"]
    col_monto = next((c for c in posibles_columnas_monto if c in df_mapeo.columns), None) or "Saldo Final"

    resultados = []
    totales_globales = {}

    # --- Procesar cada hoja ---
    for empresa, df in data_hojas.items():
        col_cuenta_balance = next((c for c in posibles_columnas_cuenta if c in df.columns), None)
        if not col_cuenta_balance:
            continue

        df_merged = df.merge(
            df_mapeo[["Descripción", "CLASIFICACION", "CATEGORIA"]],
            on="Descripción",
            how="left"
        )

        df_merged[col_monto] = pd.to_numeric(df_merged[col_monto], errors="coerce").fillna(0)
        resumen = df_merged.groupby(["CLASIFICACION", "CATEGORIA"])[col_monto].sum().reset_index()
        resumen.rename(columns={col_monto: empresa}, inplace=True)
        resultados.append(resumen)

    # --- Consolidar todas las empresas ---
    from functools import reduce
    df_final = reduce(lambda left, right: pd.merge(left, right, on=["CLASIFICACION", "CATEGORIA"], how="outer"), resultados).fillna(0)
    df_final["TOTAL ACUMULADO"] = df_final[[c for c in df_final.columns if c not in ["CLASIFICACION", "CATEGORIA"]]].sum(axis=1)

    # --- Mostrar tablas por clasificación ---
    for clasif in ["ACTIVO", "PASIVO", "CAPITAL"]:
        df_clasif = df_final[df_final["CLASIFICACION"] == clasif].copy()
        if df_clasif.empty:
            continue

        subtotal = pd.DataFrame({
            "CLASIFICACION": [clasif],
            "CATEGORIA": [f"TOTAL {clasif}"]
        })

        for col in [c for c in df_final.columns if c not in ["CLASIFICACION", "CATEGORIA"]]:
            subtotal[col] = df_clasif[col].sum()

        df_clasif = pd.concat([df_clasif, subtotal], ignore_index=True)
        totales_globales[clasif] = float(subtotal["TOTAL ACUMULADO"])

        # Formateo
        for col in [c for c in df_clasif.columns if c not in ["CLASIFICACION", "CATEGORIA"]]:
            df_clasif[col] = df_clasif[col].apply(lambda x: f"${x:,.2f}")

        with st.expander(f"🔹 {clasif}"):
            st.dataframe(df_clasif.drop(columns=["CLASIFICACION"]), use_container_width=True, hide_index=True)

    # --- Crear tabla resumen ---
    if all(k in totales_globales for k in ["ACTIVO", "PASIVO", "CAPITAL"]):
        total_activo = totales_globales["ACTIVO"]
        total_pasivo = totales_globales["PASIVO"]
        total_capital = totales_globales["CAPITAL"]
        balance = total_activo + total_pasivo + total_capital

        resumen_final = pd.DataFrame({
            "Concepto": ["TOTAL ACTIVO", "TOTAL PASIVO", "TOTAL CAPITAL", "DIFERENCIA (Debe ser 0)"],
            "Monto Total": [
                f"${total_activo:,.2f}",
                f"${total_pasivo:,.2f}",
                f"${total_capital:,.2f}",
                f"${balance:,.2f}"
            ]
        })

        st.markdown("### ⚖️ **Resumen del Balance General Consolidado**")
        st.dataframe(resumen_final, use_container_width=True, hide_index=True)

        if abs(balance) < 1:
            st.success("✅ El balance general está cuadrado (ACTIVO = PASIVO + CAPITAL).")
        else:
            st.error("❌ El balance no cuadra. Revisa los saldos por empresa.")

#tabla ingresos y egresos por empresa
def tabla_Ingresos_Egresos(balance_url):
    st.write("📊 **Ingresos, Gastos y Utilidad del Eje**")
    hojas_empresas = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]
    try:
        xls = pd.ExcelFile(balance_url)
    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
        return

    data_empresas = []
    for hoja in hojas_empresas:
        if hoja in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=hoja)
            df_merged = df.merge(
                df_mapeo[["Descripción", "CLASIFICACION", "CATEGORIA"]],
                on="Descripción",
                how="left"
            )

            posibles_columnas_monto = ["Saldo final"]
            col_monto = next((c for c in posibles_columnas_monto if c in df_merged.columns), None)
            if not col_monto:
                continue

            df_merged[col_monto] = pd.to_numeric(df_merged[col_monto], errors="coerce").fillna(0)
            df_filtrado = df_merged[df_merged["CLASIFICACION"].isin(["INGRESO", "GASTOS"])]
            resumen = (
                df_filtrado.groupby("CLASIFICACION")[col_monto]
                .sum()
                .reset_index()
            )
            resumen = resumen.set_index("CLASIFICACION").reindex(["INGRESO", "GASTOS"]).fillna(0).reset_index()
            utilidad = resumen.loc[resumen["CLASIFICACION"] == "INGRESO", col_monto].values[0] - \
                       resumen.loc[resumen["CLASIFICACION"] == "GASTOS", col_monto].values[0]
            resumen = pd.concat([
                resumen,
                pd.DataFrame({"CLASIFICACION": ["UTILIDAD DEL EJE"], col_monto: [utilidad]})
            ])

            data_empresas[hoja] = resumen.rename(columns={col_monto: hoja})
    if not data_empresas:
        st.warning("⚠️ No se encontraron datos válidos en las hojas especificadas.")
        return

    df_final = None
    for empresa, df_emp in data_empresas.items():
        if df_final is None:
            df_final = df_emp
        else:
            df_final = pd.merge(df_final, df_emp, on=["CLASIFICACION"], how="outer")
    df_final["ACUMULADO"] = df_final[hojas_empresas].sum(axis=1)
    for col in hojas_empresas + ["ACUMULADO"]:
        df_final[col] = df_final[col].apply(lambda x: f"${x:,.2f}")
    orden = ["INGRESO", "GASTOS", "UTILIDAD DEL EJE"]
    df_final["CLASIFICACION"] = pd.Categorical(df_final["CLASIFICACION"], categories=orden, ordered=True)
    df_final = df_final.sort_values("CLASIFICACION")

    st.dataframe(
        df_final,
        use_container_width=True,
        hide_index=True
    )

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_final.to_excel(writer, index=False, sheet_name="Ingresos_Egresos")
    st.download_button(
        label="💾 Descargar tabla consolidada en Excel",
        data=output.getvalue(),
        file_name="Ingresos_Egresos_Consolidado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def tabla_ingresos_egresos2():
    st.write("📊 Ingresos, Gastos y Utilidad del Eje (con DEBE/HABER y DEBE_2/HABER_2 automáticos)")

    hojas_empresas = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]

    try:
        xls_balance = pd.ExcelFile(balance_url)
        xls_manual = pd.ExcelFile(st.secrets["urls"]["Info Manual"])
    except Exception as e:
        st.error(f"❌ Error al leer los archivos: {e}")
        return
    try:
        df_manual = pd.read_excel(xls_manual, sheet_name="INTEREMPRESAS", header=None)
        df_manual = df_manual.fillna("")
        fila_total = df_manual[df_manual.apply(lambda r: r.astype(str).str.contains("Total general", case=False).any(), axis=1)]
        if fila_total.empty:
            st.warning("⚠️ No se encontró la fila 'Total general' en la hoja INTEREMPRESAS.")
            return

        fila_idx = fila_total.index[0]
        total_egreso = df_manual.iloc[fila_idx, 1]
        total_ingreso = df_manual.iloc[fila_idx, 2]
        total_egreso = float(str(total_egreso).replace("$", "").replace(",", "").strip() or 0)
        total_ingreso = float(str(total_ingreso).replace("$", "").replace(",", "").strip() or 0)

    except Exception as e:
        st.error(f"❌ Error al leer los totales desde Info Manual: {e}")
        return
    data_empresas = {}
    for hoja in hojas_empresas:
        if hoja in xls_balance.sheet_names:
            df = pd.read_excel(xls_balance, sheet_name=hoja)
            df_merged = df.merge(
                df_mapeo[["Descripción", "CLASIFICACION", "CATEGORIA"]],
                on="Descripción",
                how="left"
            )

            col_monto = next((c for c in ["Saldo final"] if c in df_merged.columns), None)
            if not col_monto:
                continue

            df_merged[col_monto] = pd.to_numeric(df_merged[col_monto], errors="coerce").fillna(0)
            df_filtrado = df_merged[df_merged["CLASIFICACION"].isin(["INGRESO", "GASTOS"])]

            resumen = (
                df_filtrado.groupby("CLASIFICACION")[col_monto]
                .sum()
                .reset_index()
            )
            resumen = resumen.set_index("CLASIFICACION").reindex(["INGRESO", "GASTOS"]).fillna(0).reset_index()
            utilidad = (
                resumen.loc[resumen["CLASIFICACION"] == "INGRESO", col_monto].values[0]
                - resumen.loc[resumen["CLASIFICACION"] == "GASTOS", col_monto].values[0]
            )

            resumen = pd.concat([
                resumen,
                pd.DataFrame({"CLASIFICACION": ["UTILIDAD DEL EJE"], col_monto: [utilidad]})
            ])

            data_empresas[hoja] = resumen.rename(columns={col_monto: hoja})

    df_final = None
    for empresa, df_emp in data_empresas.items():
        if df_final is None:
            df_final = df_emp
        else:
            df_final = pd.merge(df_final, df_emp, on=["CLASIFICACION"], how="outer")
    df_final["RESULTADO"] = df_final[hojas_empresas].sum(axis=1)
    df_final["DEBE"] = 0.0
    df_final["HABER"] = 0.0
    df_final["TOTALES"] = 0.0
    df_final["DEBE_2"] = 0.0
    df_final["HABER_2"] = 0.0
    df_final["TOTAL_2"] = 0.0
    df_final.loc[df_final["CLASIFICACION"] == "INGRESO", "DEBE"] = total_ingreso
    df_final.loc[df_final["CLASIFICACION"] == "GASTOS", "HABER"] = total_egreso
    df_final["TOTALES"] = df_final["RESULTADO"] + df_final["DEBE"] - df_final["HABER"]
    try:
        global provision_de_gastos, total_pendiente_facturar
        df_final.loc[df_final["CLASIFICACION"] == "GASTOS", "DEBE_2"] = float(provision_de_gastos)
        df_final.loc[df_final["CLASIFICACION"] == "INGRESO", "HABER_2"] = float(total_pendiente_facturar)
    except NameError:
        st.info("ℹ️ Variables 'provision_de_gastos' y 'total_pendiente_facturar' no definidas aún, se dejan en 0.")
        df_final["DEBE_2"] = 0.0
        df_final["HABER_2"] = 0.0

    df_final["TOTAL_2"] = df_final["TOTALES"] + df_final["DEBE_2"] - df_final["HABER_2"]
    for col in ["RESULTADO", "DEBE", "HABER", "TOTALES", "DEBE_2", "HABER_2", "TOTAL_2"]:
        df_final[col] = df_final[col].apply(lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) and x != 0 else "")

    orden = ["INGRESO", "GASTOS", "UTILIDAD DEL EJE"]
    df_final["CLASIFICACION"] = pd.Categorical(df_final["CLASIFICACION"], categories=orden, ordered=True)
    df_final = df_final.sort_values("CLASIFICACION")

    st.dataframe(df_final, use_container_width=True, hide_index=True)

    st.download_button(
        label="💾 Descargar tabla Ingresos-Egresos (Excel)",
        data=output.getvalue(),
        file_name="Ingresos_Egresos_InfoManual.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def tabla_servicios_no_facturados():
    st.subheader("Servicios No Facturados")

    # --- Variable manual editable ---
    ingresos_reales_4t = st.number_input(
        "Ingresos Reales",
        min_value=0.0,
        value=515_904_930.0,
        step=1_000_000.0,
        format="%.2f"
    )

    hojas_empresas = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]
    try:
        xls_balance = pd.ExcelFile(balance_url)
        xls_manual = pd.ExcelFile(st.secrets["urls"]["Info Manual"])
    except Exception as e:
        st.error(f"❌ Error al leer los archivos: {e}")
        return

    # --- Extraer DEBE / HABER desde Info Manual (hoja INTEREMPRESAS) ---
    try:
        df_manual = pd.read_excel(xls_manual, sheet_name="INTEREMPRESAS", header=None)
        df_manual = df_manual.fillna("")
        fila_total = df_manual[df_manual.apply(
            lambda r: r.astype(str).str.contains("Total general", case=False).any(), axis=1
        )]

        if fila_total.empty:
            st.warning("⚠️ No se encontró la fila 'Total general' en la hoja INTEREMPRESAS.")
            return

        fila_idx = fila_total.index[0]
        total_egreso = df_manual.iloc[fila_idx, 1]  
        total_ingreso = df_manual.iloc[fila_idx, 2]  
        total_egreso = float(str(total_egreso).replace("$", "").replace(",", "").strip() or 0)
        total_ingreso = float(str(total_ingreso).replace("$", "").replace(",", "").strip() or 0)

    except Exception as e:
        st.error(f"❌ Error al leer los totales desde Info Manual: {e}")
        return

    # --- Consolidar Ingresos y Gastos por empresa ---
    data_empresas = []
    for hoja in hojas_empresas:
        if hoja in xls_balance.sheet_names:
            df = pd.read_excel(xls_balance, sheet_name=hoja)
            df_merged = df.merge(
                df_mapeo[["Descripción", "CLASIFICACION", "CATEGORIA"]],
                on="Descripción",
                how="left"
            )

            col_monto = next((c for c in ["Saldo final"] if c in df_merged.columns), None)
            if not col_monto:
                continue

            df_merged[col_monto] = pd.to_numeric(df_merged[col_monto], errors="coerce").fillna(0)
            df_filtrado = df_merged[df_merged["CLASIFICACION"].isin(["INGRESO", "GASTOS"])]

            resumen = (
                df_filtrado.groupby("CLASIFICACION")[col_monto]
                .sum()
                .reset_index()
            )

            resumen = resumen.set_index("CLASIFICACION").reindex(["INGRESO", "GASTOS"]).fillna(0).reset_index()
            utilidad = resumen.loc[resumen["CLASIFICACION"] == "INGRESO", col_monto].values[0] - \
                       resumen.loc[resumen["CLASIFICACION"] == "GASTOS", col_monto].values[0]

            resumen = pd.concat([
                resumen,
                pd.DataFrame({"CLASIFICACION": ["UTILIDAD DEL EJE"], col_monto: [utilidad]})
            ])

            data_empresas.append(resumen.rename(columns={col_monto: hoja}))

    # --- Unir todas las empresas ---
    if not data_empresas:
        st.warning("⚠️ No se encontraron datos válidos en las hojas del balance.")
        return

    df_final = pd.concat(data_empresas)
    df_final = df_final.groupby("CLASIFICACION").sum().reset_index()

    # --- Calcular acumulado de ingresos ---
    ingresos_acumulados = df_final.loc[df_final["CLASIFICACION"] == "INGRESO"].iloc[:, 1:].sum(axis=1).values[0]

    # --- Calcular valores contables ---
    ingresos_facturados_4t = ingresos_acumulados - total_ingreso
    total_pendiente_facturar = ingresos_reales_4t - ingresos_facturados_4t

    # --- Calcular IVA y total por facturar ---
    tasa_iva = 0.16
    iva_por_pagar = total_pendiente_facturar * tasa_iva
    total_por_facturar = total_pendiente_facturar + iva_por_pagar

    # --- Crear tabla resumen ---
    df_tabla = pd.DataFrame({
        "Concepto": [
            "Ingresos Reales",
            "Ingresos Facturados",
            "Pendiente por Facturar",
            "IVA por Pagar (16%)",
            "Total por Facturar"
        ],
        "Monto (MXN)": [
            ingresos_reales_4t,
            ingresos_facturados_4t,
            total_pendiente_facturar,
            iva_por_pagar,
            total_por_facturar
        ]
    })

    df_tabla["Monto (MXN)"] = df_tabla["Monto (MXN)"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(df_tabla, use_container_width=True, hide_index=True)
    return df_tabla

def tabla_ajuste_gastos():
    st.subheader("📊 Ajuste de Gastos y Provisiones")

    # --- Inputs editables ---
    gasto_real = st.number_input(
        min_value=0.0,
        value=0.0,
        step=100000.0,
        format="%.2f"
    )

    impuestos = st.number_input(
        min_value=0.0,
        value=0.0,
        step=100000.0,
        format="%.2f"
    )

    # --- Cargar totales desde Info Manual ---
    try:
        xls_manual = pd.ExcelFile(st.secrets["urls"]["Info Manual"])
        df_manual = pd.read_excel(xls_manual, sheet_name="INTEREMPRESAS", header=None)
        df_manual = df_manual.fillna("")

        fila_total = df_manual[df_manual.apply(
            lambda r: r.astype(str).str.contains("Total general", case=False).any(), axis=1
        )]

        if fila_total.empty:
            st.warning("⚠️ No se encontró la fila 'Total general' en la hoja INTEREMPRESAS.")
            return

        fila_idx = fila_total.index[0]
        total_egreso = df_manual.iloc[fila_idx, 1]  # Columna B (Egreso)
        total_egreso = float(str(total_egreso).replace("$", "").replace(",", "").strip() or 0)

    except Exception as e:
        st.error(f"❌ Error al leer los totales desde Info Manual: {e}")
        return
    try:
        xls_balance = pd.ExcelFile(balance_url)
        hojas_empresas = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]
        data_empresas = []

        for hoja in hojas_empresas:
            if hoja in xls_balance.sheet_names:
                df = pd.read_excel(xls_balance, sheet_name=hoja)
                df_merged = df.merge(
                    df_mapeo[["Descripción", "CLASIFICACION", "CATEGORIA"]],
                    on="Descripción",
                    how="left"
                )

                col_monto = next((c for c in ["Saldo final"] if c in df_merged.columns), None)
                if not col_monto:
                    continue

                df_merged[col_monto] = pd.to_numeric(df_merged[col_monto], errors="coerce").fillna(0)
                gastos = df_merged[df_merged["CLASIFICACION"] == "GASTOS"][col_monto].sum()
                data_empresas.append(gastos)

        acumulado = sum(data_empresas)
    except Exception as e:
        st.warning(f"⚠️ No se pudieron calcular los gastos acumulados: {e}")
        acumulado = 0.0

    # --- Cálculos principales ---
    gasto_facturado = acumulado - total_egreso
    provision_de_gastos = gasto_real + impuestos - gasto_facturado

    df_tabla = pd.DataFrame({
        "Concepto": [
            "Gasto Real",
            "Impuestos",
            "Gasto Facturado",
            "Provisión de Gastos"
        ],
        "Monto (MXN)": [
            gasto_real,
            impuestos,
            gasto_facturado,
            provision_de_gastos
        ]
    })

    df_tabla["Monto (MXN)"] = df_tabla["Monto (MXN)"].apply(lambda x: f"${x:,.2f}")

def tabla_inversiones():
    st.subheader("📊 Inversiones entre Compañías (Activos)")

    # === Variables originales que tú definiste ===
    inversiones_dict = {
        "HDL-WH": {"hoja": "HOLDING", "descripcion": "INVERSION ESGARI WAREHOUSING"},
        "EHM-WH": {"hoja": "EHM", "descripcion": "INVERSION ESGARI WAREHOUSING"},
        "FWD-WH": {"hoja": "FWD", "descripcion": "ACCIONES ESGARI WAREHOUSING & MANUFACTURING"},
        "EHM-FWD": {"hoja": "EHM", "descripcion": "INVERSION ESGARI FORWARDING"},
        "EHM-UBIKARGA": {"hoja": "EHM", "descripcion": "INVERSION UBIKARGA"},
        "EHM-GREEN": {"hoja": "EHM", "descripcion": "INVERSION ESGARI GREEN"},
        "EHM-RESA": {"hoja": "EHM", "descripcion": "INVERSION RESA MULTIMODAL"},
        "EHM-HOLDING": {"hoja": "EHM", "descripcion": "INVERSION ESGARI HOLDING"},
    }

    try:
        xls_balance = pd.ExcelFile(balance_url)
    except Exception as e:
        st.error(f"❌ Error al leer el archivo del balance: {e}")
        return

    # === Capital social total por empresa ===
    TCSW = {"hoja": "WH", "clasificacion": "CAPITAL"}
    TCSF = {"hoja": "FWD", "clasificacion": "CAPITAL"}
    TCSU = {"hoja": "UBIKARGA", "clasificacion": "CAPITAL"}
    TCSG = {"hoja": "GREEN", "clasificacion": "CAPITAL"}
    TCSR = {"hoja": "RESA", "clasificacion": "CAPITAL"}
    TCSH = {"hoja": "HOLDING", "clasificacion": "CAPITAL"}

    data_inversiones = []

    # === Buscar montos de inversión ===
    for clave, info in inversiones_dict.items():
        hoja = info["hoja"]
        descripcion = info["descripcion"]

        if hoja not in xls_balance.sheet_names:
            continue

        df = pd.read_excel(xls_balance, sheet_name=hoja)
        posibles_columnas = ["Descripción", "Cuenta", "Concepto"]
        col_desc = next((c for c in posibles_columnas if c in df.columns), None)
        col_monto = next((c for c in ["Saldo final", "Monto", "Importe"] if c in df.columns), None)

        if not col_desc or not col_monto:
            continue

        df[col_monto] = pd.to_numeric(df[col_monto], errors="coerce").fillna(0)
        df[col_desc] = df[col_desc].astype(str).str.strip().str.upper()

        mask = df[col_desc].str.contains(descripcion.upper(), na=False)
        monto = df.loc[mask, col_monto].sum() if mask.any() else 0

        data_inversiones.append({
            "VARIABLE": clave,
            "DESCRIPCIÓN": descripcion,
            "ACTIVO": monto,
            "SOCIAL": 0.0,  # se llenará después
            "TOTALES": monto
        })

    if not data_inversiones:
        st.warning("⚠️ No se encontraron inversiones con las descripciones indicadas.")
        return

    df_inv = pd.DataFrame(data_inversiones)

    # === Asignar los valores del capital social ===
    for i, row in df_inv.iterrows():
        clave = row["VARIABLE"]
        if clave == "HDL-WH":
            df_inv.at[i, "SOCIAL"] = 14404988.06
        else:
            df_inv.at[i, "SOCIAL"] = row["ACTIVO"]

        df_inv.at[i, "TOTALES"] = row["ACTIVO"] - df_inv.at[i, "SOCIAL"]

    # === Agrupar por bloques ===
    bloques = {
        "HDL-WH, EHM-WH, FWD-WH": ["HDL-WH", "EHM-WH", "FWD-WH"],
        "EHM-FWD": ["EHM-FWD"],
        "EHM-UBIKARGA": ["EHM-UBIKARGA"],
        "EHM-GREEN": ["EHM-GREEN"],
        "EHM-RESA": ["EHM-RESA"],
        "EHM-HOLDING": ["EHM-HOLDING"]
    }

    tabla_final = []
    total_activo = 0
    total_social = 0
    total_total = 0

    for bloque, claves in bloques.items():
        bloque_df = df_inv[df_inv["VARIABLE"].isin(claves)]
        subtotal_activo = bloque_df["ACTIVO"].sum()
        subtotal_social = bloque_df["SOCIAL"].sum()
        subtotal_total = bloque_df["TOTALES"].sum()

        tabla_final.extend(bloque_df.to_dict("records"))
        tabla_final.append({
            "VARIABLE": "",
            "DESCRIPCIÓN": "TOTAL CAPITAL SOCIAL",
            "ACTIVO": subtotal_activo,
            "SOCIAL": subtotal_social,
            "TOTALES": subtotal_total
        })

        total_activo += subtotal_activo
        total_social += subtotal_social
        total_total += subtotal_total

    UTAC = total_social  
    UTILIDAD_EJERCICIO = 0.00
    EHM_HOLDING = df_inv.loc[df_inv["VARIABLE"] == "EHM-HOLDING", "ACTIVO"].sum()
    total_inversiones = EHM_HOLDING + UTAC
    GOODWILL = (total_activo+ total_social)*-1
    TOTAL_CAPITAL_SOCIAL_FINAL = total_inversiones + GOODWILL

    # === Agregar filas finales ===
    tabla_final.append({
        "VARIABLE": "",
        "DESCRIPCIÓN": "UTILIDADES ACUM METODO DE PARTICIPACION",
        "ACTIVO": 0,
        "SOCIAL": UTAC,
        "TOTALES": 0
    })
    tabla_final.append({
        "VARIABLE": "",
        "DESCRIPCIÓN": "UTILIDADES DEL EJERCICIO",
        "ACTIVO": 0,
        "SOCIAL": UTILIDAD_EJERCICIO,
        "TOTALES": 0
    })
    tabla_final.append({
        "VARIABLE": "",
        "DESCRIPCIÓN": "TOTAL",
        "ACTIVO": total_activo,
        "SOCIAL": total_social + UTILIDAD_EJERCICIO,
        "TOTALES": total_total
    })
    tabla_final.append({
        "VARIABLE": "",
        "DESCRIPCIÓN": "EHM HOLDING GOODWILL (Intangibles)",
        "ACTIVO": GOODWILL,
        "SOCIAL": 0,
        "TOTALES": GOODWILL
    })
    tabla_final.append({
        "VARIABLE": "",
        "DESCRIPCIÓN": "TOTAL CAPITAL SOCIAL",
        "ACTIVO": total_activo,
        "SOCIAL": TOTAL_CAPITAL_SOCIAL_FINAL,
        "TOTALES": 0
    })

    df_final = pd.DataFrame(tabla_final)

    # === Mostrar tabla final ===
    st.dataframe(
        df_final.style.format({
            "ACTIVO": "${:,.2f}",
            "SOCIAL": "${:,.2f}",
            "TOTALES": "${:,.2f}",
        }),
        use_container_width=True,
        hide_index=True
    )

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_inv.to_excel(writer, index=False, sheet_name="Inversiones")
        df_total.to_excel(writer, index=False, sheet_name="Totales")
        workbook = writer.book
        for sheet in ["Inversiones", "Totales"]:
            worksheet = writer.sheets[sheet]
            worksheet.set_h_pagebreaks([])
            worksheet.set_v_pagebreaks([])

    st.download_button(
        label="💾 Descargar tabla de inversiones en Excel",
        data=output.getvalue(),
        file_name="Inversiones_Entre_Compañias.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    return total_activo, total_social, GOODWILL
total_activo, total_social, GOODWILL = tabla_inversiones()


def tabla_balance_acumulado(total_social, total_inversiones, GOODWILL):
    st.write("📊 **BALANCE GENERAL ACUMULADO**")
    # --- Variables externas o calculadas en otras funciones ---
    iva_por_pagar = 0.0  # o el valor que definas en otra parte

    hojas_empresas = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]

    try:
        xls = pd.ExcelFile(balance_url)
    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
        return

    data_empresas = []
    for hoja in hojas_empresas:
        if hoja in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=hoja)
            df_merged = df.merge(
                df_mapeo[["Descripción", "CLASIFICACION", "CATEGORIA"]],
                on="Descripción",
                how="left"
            )

            posibles_columnas_monto = ["Saldo final"]
            col_monto = next((c for c in posibles_columnas_monto if c in df_merged.columns), None)
            if not col_monto:
                continue

            df_merged[col_monto] = pd.to_numeric(df_merged[col_monto], errors="coerce").fillna(0)
            df_filtrado = df_merged[df_merged["CLASIFICACION"].isin(["ACTIVO", "PASIVO", "CAPITAL"])]

            resumen = (
                df_filtrado.groupby(["CLASIFICACION", "CATEGORIA"])[col_monto]
                .sum()
                .reset_index()
            )
            data_empresas.append(resumen)

    if not data_empresas:
        st.warning("⚠️ No se encontraron datos en las hojas especificadas.")
        return

    # Consolidar todas las hojas
    from functools import reduce
    df_total = reduce(lambda left, right: pd.merge(left, right, on=["CLASIFICACION", "CATEGORIA"], how="outer"), data_empresas)
    df_total = df_total.fillna(0)
    df_total["ACUMULADO"] = df_total[[c for c in df_total.columns if c not in ["CLASIFICACION", "CATEGORIA"]]].sum(axis=1)
    df_total = df_total.rename(columns={"CATEGORIA": "CUENTA"})

    # Inicializar columnas
    df_total["DEBE"] = 0.0
    df_total["HABER"] = 0.0
    df_total["MANUAL"] = 0.0

    # Ajustes específicos por cuenta
    df_total.loc[df_total["CUENTA"].str.contains("CUENTAS POR COBRAR NO FACTURADAS", case=False), "DEBE"] = df_total["ACUMULADO"]
    df_total.loc[df_total["CUENTA"].str.contains("DEUDORES RELACIONADOS|IVA ACREDITABLE", case=False), "HABER"] = df_total["ACUMULADO"]

    # Impuestos diferidos
    activo_imp_dif = df_total.loc[
        (df_total["CLASIFICACION"] == "ACTIVO") &
        (df_total["CUENTA"].str.contains("IMPUESTOS DIFERIDOS", case=False)),
        "HABER"
    ].sum()
    df_total.loc[
        (df_total["CLASIFICACION"] == "PASIVO") &
        (df_total["CUENTA"].str.contains("IMPUESTOS DIFERIDOS", case=False)),
        "DEBE"
    ] = activo_imp_dif

    # IVA trasladado
    iva_acred = df_total.loc[df_total["CUENTA"].str.contains("IVA ACREDITABLE", case=False), "ACUMULADO"].sum()
    df_total.loc[df_total["CUENTA"].str.contains("IVA POR TRASLADAR", case=False), "DEBE"] = iva_acred
    df_total.loc[df_total["CUENTA"].str.contains("IVA POR TRASLADAR", case=False), "HABER"] = iva_por_pagar

    # Acreedores relacionados
    deud_rel = df_total.loc[df_total["CUENTA"].str.contains("DEUDORES RELACIONADOS", case=False), "ACUMULADO"].sum()
    df_total.loc[df_total["CUENTA"].str.contains("ACREEDORES RELACIONADOS", case=False), "DEBE"] = deud_rel * -1

    # Goodwill
    df_total.loc[df_total["CUENTA"].str.contains("GOODWILL", case=False), "DEBE"] = GOODWILL

    # Capital social: agregar suma de total_social + total_inversiones en el DEBE
    total_capital_social = total_social + total_inversiones
    df_total.loc[df_total["CUENTA"].str.contains("CAPITAL SOCIAL", case=False), "DEBE"] = total_capital_social

    # Crear estructura jerárquica
    filas = []
    for clasif in ["ACTIVO", "PASIVO", "CAPITAL"]:
        df_clasif = df_total[df_total["CLASIFICACION"] == clasif].copy()
        if df_clasif.empty:
            continue

        subtotal = {
            "CLASIFICACION": clasif,
            "CUENTA": f"TOTAL {clasif}",
            "ACUMULADO": df_clasif["ACUMULADO"].sum(),
            "DEBE": df_clasif["DEBE"].sum(),
            "HABER": df_clasif["HABER"].sum(),
            "MANUAL": df_clasif["MANUAL"].sum(),
            "TOTALES": 0.0
        }

        filas.append({
            "CLASIFICACION": clasif,
            "CUENTA": clasif,
            "ACUMULADO": "",
            "DEBE": 0.0,
            "HABER": 0.0,
            "MANUAL": 0.0,
            "TOTALES": ""
        })
        filas.extend(df_clasif.to_dict("records"))
        filas.append(subtotal)

    df_final = pd.DataFrame(filas)

    # Reemplazar vacíos por 0 para edición
    for col in ["DEBE", "HABER", "MANUAL"]:
        df_final[col] = pd.to_numeric(df_final[col], errors="coerce").fillna(0.0)

    # Cálculo inicial de TOTALES
    df_final["TOTALES"] = (
        df_final["ACUMULADO"].replace("", 0).astype(float)
        + df_final["DEBE"].astype(float)
        - df_final["HABER"].astype(float)
        + df_final["MANUAL"].astype(float)
    )

    # Editor interactivo
    st.markdown("🧾 **Puedes editar DEBE, HABER o MANUAL para ajustar los totales:**")
    df_editable = st.data_editor(
        df_final,
        num_rows="dynamic",
        column_config={
            "ACUMULADO": st.column_config.NumberColumn("ACUMULADO", format="%.2f", disabled=True),
            "DEBE": st.column_config.NumberColumn("DEBE", format="%.2f"),
            "HABER": st.column_config.NumberColumn("HABER", format="%.2f"),
            "MANUAL": st.column_config.NumberColumn("MANUAL", format="%.2f"),
            "TOTALES": st.column_config.NumberColumn("TOTALES", format="%.2f", disabled=True),
            "CLASIFICACION": st.column_config.TextColumn("CLASIFICACIÓN", disabled=True),
            "CUENTA": st.column_config.TextColumn("CUENTA", disabled=True),
        },
        use_container_width=True,
        hide_index=True,
        key="balance_editor",
    )

    # Recalcular TOTALES tras edición
    for col in ["DEBE", "HABER", "MANUAL"]:
        df_editable[col] = pd.to_numeric(df_editable[col], errors="coerce").fillna(0.0)

    df_editable["TOTALES"] = (
        df_editable["ACUMULADO"].replace("", 0).astype(float)
        + df_editable["DEBE"].astype(float)
        - df_editable["HABER"].astype(float)
        + df_editable["MANUAL"].astype(float)
    )

    # Mostrar tabla final
    st.dataframe(
        df_editable.style.format({
            "ACUMULADO": "${:,.2f}",
            "DEBE": "${:,.2f}",
            "HABER": "${:,.2f}",
            "MANUAL": "${:,.2f}",
            "TOTALES": "${:,.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    return df_editable

def tabla_BALANCE_FINAL(df_editable):
    st.subheader("📊 BALANCE FINAL CONSOLIDADO")
    df_totales = df_editable[["CUENTA", "TOTALES"]].copy()

    total_activo = df_editable.loc[df_editable["CUENTA"] == "TOTAL ACTIVO", "TOTALES"].sum()
    total_pasivo = df_editable.loc[df_editable["CUENTA"] == "TOTAL PASIVO", "TOTALES"].sum()
    total_capital = df_editable.loc[df_editable["CUENTA"] == "TOTAL CAPITAL", "TOTALES"].sum()
    balance_final = total_activo + total_pasivo + total_capital

    # --- Crear DataFrame resumen ---
    df_total = pd.DataFrame({
        "CUENTA": ["TOTAL ACTIVO", "TOTAL PASIVO", "TOTAL CAPITAL", "BALANCE FINAL"],
        "TOTALES": [total_activo, total_pasivo, total_capital, balance_final]
    })

    # --- Actualizar o crear variable global ---
    global DEF_BALANCE_FINAL
    if "DEF_BALANCE_FINAL" in globals():
        DEF_BALANCE_FINAL = DEF_BALANCE_FINAL.merge(
            df_total,
            on="CUENTA",
            how="left",
            suffixes=('', '_nuevo')
        )
        DEF_BALANCE_FINAL["TOTALES"] = DEF_BALANCE_FINAL["TOTALES_nuevo"].combine_first(DEF_BALANCE_FINAL["TOTALES"])
        DEF_BALANCE_FINAL.drop(columns=["TOTALES_nuevo"], inplace=True)
    else:
        DEF_BALANCE_FINAL = df_total.copy()

    st.dataframe(
        DEF_BALANCE_FINAL.style.format({"TOTALES": "${:,.2f}"}),
        use_container_width=True,
        hide_index=True
    )

    if abs(balance_final) < 1:
        st.success("✅ El balance general está cuadrado")
    else:
        st.error("❌ El balance no cuadra. Revisa los montos.")

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        DEF_BALANCE_FINAL.to_excel(writer, index=False, sheet_name="Balance_Final")

        workbook = writer.book
        worksheet = writer.sheets["Balance_Final"]
        money_format = workbook.add_format({'num_format': '$#,##0.00', 'align': 'right'})
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D9E1F2'})

        worksheet.set_row(0, None, header_format)
        worksheet.set_column("A:A", 25)
        worksheet.set_column("B:B", 20, money_format)
        worksheet.set_h_pagebreaks([])
        worksheet.set_v_pagebreaks([])
        worksheet.fit_to_pages(1, 0)

    st.download_button(
        label="💾 Descargar Balance Final en Excel",
        data=output.getvalue(),
        file_name="Balance_Final.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if selected == "BALANCE POR EMPRESA":
    tabla_balance_por_empresa()

elif selected == "BALANCE GENERAL ACUMULADO":
    tabla_balance_acumulado()
    tabla_Ingresos_Egresos()
    tabla_ingresos_egresos2()
    tabla_servicios_no_facturados()
    tabla_ajuste_gastos()
    tabla_inversiones()

elif selected == "BALANCE FINAL":

    tabla_BALANCE_FINAL()






