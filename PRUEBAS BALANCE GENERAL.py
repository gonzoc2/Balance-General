import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import BytesIO
import xlsxwriter
from functools import reduce
from streamlit_option_menu import option_menu


# --- Configuración de la página ---
st.set_page_config(
    page_title="Esgari 360",
    page_icon="🚚",  # Icono de camión
    layout="wide"
)

logo_base64 = """[PEGA AQUÍ TU BASE64 COMPLETO]"""
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
    st.subheader("📊 Balance General Consolidado por Empresa")

    @st.cache_data(show_spinner="Cargando mapeo de cuentas...")
    def cargar_mapeo(url):
        r = requests.get(url)
        r.raise_for_status()
        file = BytesIO(r.content)
        df_mapeo = pd.read_excel(file, sheet_name=None, engine="openpyxl")
        if isinstance(df_mapeo, dict):
            df_mapeo = list(df_mapeo.values())[0]
        df_mapeo.columns = df_mapeo.columns.str.strip()
        return df_mapeo

    @st.cache_data(show_spinner="Cargando hojas del balance...")
    def cargar_hojas(url, hojas):
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
                st.warning(f"No se pudo leer la hoja {hoja}: {e}")
        return data

    hojas_empresas = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]
    df_mapeo = cargar_mapeo(mapeo_url)
    data_hojas = cargar_hojas(balance_url, hojas_empresas)

    posibles_columnas_cuenta = ["Cuenta", "Descripción"]
    col_cuenta_mapeo = next((c for c in posibles_columnas_cuenta if c in df_mapeo.columns), None)
    posibles_columnas_monto = ["Saldo Final"]
    col_monto = posibles_columnas_monto[0]

    resultados = []
    totales_globales = {} 

    for empresa, df in data_hojas.items():
        col_cuenta_balance = next((c for c in posibles_columnas_cuenta if c in df.columns), None)
        if not col_cuenta_balance:
            continue
        df_merged = df.merge(
            df_mapeo[[col_cuenta_mapeo, "CLASIFICACION", "CATEGORIA"]],
            left_on=col_cuenta_balance,
            right_on=col_cuenta_mapeo,
            how="left"
        )
        df_merged[col_monto] = pd.to_numeric(df_merged[col_monto], errors="coerce").fillna(0)
        resumen = df_merged.groupby(["CLASIFICACION", "CATEGORIA"])[col_monto].sum().reset_index()
        resumen.rename(columns={col_monto: empresa}, inplace=True)
        resultados.append(resumen)

    df_final = reduce(lambda left, right: pd.merge(left, right, on=["CLASIFICACION", "CATEGORIA"], how="outer"), resultados).fillna(0)
    df_final["TOTAL ACUMULADO"] = df_final[hojas_empresas].sum(axis=1)

    for clasif in ["ACTIVO", "PASIVO", "CAPITAL"]:
        df_clasif = df_final[df_final["CLASIFICACION"] == clasif].copy()
        if df_clasif.empty:
            continue
        subtotal = pd.DataFrame({
            "CLASIFICACION": [clasif],
            "CATEGORIA": [f"TOTAL {clasif}"]
        })
        for col in hojas_empresas + ["TOTAL ACUMULADO"]:
            subtotal[col] = df_clasif[col].sum()
        df_clasif = pd.concat([df_clasif, subtotal], ignore_index=True)
        totales_globales[clasif] = float(df_clasif.loc[df_clasif["CATEGORIA"] == f"TOTAL {clasif}", "TOTAL ACUMULADO"])
        for col in hojas_empresas + ["TOTAL ACUMULADO"]:
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

        st.markdown("### 🧾 **Resumen Consolidado del Balance General**")
        st.dataframe(resumen_final, use_container_width=True, hide_index=True)

        if abs(balance) < 1:
            st.success("✅ El balance general está cuadrado (ACTIVO = PASIVO + CAPITAL).")
        else:
            st.error("❌ El balance no cuadra. Revisa los saldos por empresa.")
#tabla ingresos y egresos por empresa
def tabla_Ingresos_Egresos(balance_url):
    st.write("📊 **Ingresos, Gastos y Utilidad del Eje por Empresa (Consolidado)**")
    hojas_empresas = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]
    try:
        xls = pd.ExcelFile(balance_url)
    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
        return

    data_empresas = {}

    for hoja in hojas_empresas:
        if hoja in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=hoja)
            df_merged = df.merge(
                df_mapeo[[col_cuenta_mapeo, "CLASIFICACION", "CATEGORIA"]],
                left_on=col_cuenta_balance,
                right_on=col_cuenta_mapeo,
                how="left"
            )

            posibles_columnas_monto = ["Saldo Final"]
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
    st.write("📊 **Ingresos, Gastos y Utilidad del Eje (con DEBE y HABER automáticos desde Info Manual)**")

    # --- Archivos base ---
    hojas_empresas = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]

    try:
        xls_balance = pd.ExcelFile(balance_url)
        xls_manual = pd.ExcelFile(st.secrets["urls"]["Info Manual"])
    except Exception as e:
        st.error(f"❌ Error al leer los archivos: {e}")
        return

    # --- Extraer DEBE / HABER desde "Info Manual" (hoja INTEREMPRESAS) ---
    try:
        df_manual = pd.read_excel(xls_manual, sheet_name="INTEREMPRESAS", header=None)
        df_manual = df_manual.fillna("")
        fila_total = df_manual[df_manual.apply(lambda r: r.astype(str).str.contains("Total general", case=False).any(), axis=1)]
        if fila_total.empty:
            st.warning("⚠️ No se encontró la fila 'Total general' en la hoja INTEREMPRESAS.")
            return

        fila_idx = fila_total.index[0]
        total_egreso = df_manual.iloc[fila_idx, 1]  # Columna B (Egreso)
        total_ingreso = df_manual.iloc[fila_idx, 2]  # Columna C (Ingreso)
        total_egreso = float(str(total_egreso).replace("$", "").replace(",", "").strip() or 0)
        total_ingreso = float(str(total_ingreso).replace("$", "").replace(",", "").strip() or 0)

    except Exception as e:
        st.error(f"❌ Error al leer los totales desde Info Manual: {e}")
        return

    # --- Consolidar Ingresos y Gastos por empresa ---
    data_empresas = {}
    for hoja in hojas_empresas:
        if hoja in xls_balance.sheet_names:
            df = pd.read_excel(xls_balance, sheet_name=hoja)
            df_merged = df.merge(
                df_mapeo[[col_cuenta_mapeo, "CLASIFICACION", "CATEGORIA"]],
                left_on=col_cuenta_balance,
                right_on=col_cuenta_mapeo,
                how="left"
            )

            col_monto = next((c for c in ["Saldo Final"] if c in df_merged.columns), None)
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

    # --- Unir todas las empresas ---
    df_final = None
    for empresa, df_emp in data_empresas.items():
        if df_final is None:
            df_final = df_emp
        else:
            df_final = pd.merge(df_final, df_emp, on=["CLASIFICACION"], how="outer")

    # --- Calcular acumulado ---
    df_final["RESULTADO"] = df_final[hojas_empresas].sum(axis=1)

    # --- Crear columnas contables ---
    df_final["DEBE"] = 0.0
    df_final["HABER"] = 0.0
    df_final["TOTALES"] = 0.0

    # Asignar los valores desde Info Manual
    df_final.loc[df_final["CLASIFICACION"] == "INGRESO", "DEBE"] = total_ingreso
    df_final.loc[df_final["CLASIFICACION"] == "GASTOS", "HABER"] = total_egreso

    # Calcular totales
    df_final["TOTALES"] = df_final["RESULTADO"] + df_final["DEBE"] - df_final["HABER"]

    # --- Limitar columnas visibles ---
    df_final = df_final[["CLASIFICACION", "RESULTADO", "DEBE", "HABER", "TOTALES"]]

    # --- Formatear visualmente ---
    for col in ["RESULTADO", "DEBE", "HABER", "TOTALES"]:
        df_final[col] = df_final[col].apply(lambda x: f"${x:,.2f}" if x != 0 else "")

    orden = ["INGRESO", "GASTOS", "UTILIDAD DEL EJE"]
    df_final["CLASIFICACION"] = pd.Categorical(df_final["CLASIFICACION"], categories=orden, ordered=True)
    df_final = df_final.sort_values("CLASIFICACION")

    # --- Mostrar en Streamlit ---
    st.dataframe(df_final, use_container_width=True, hide_index=True)

    # --- Exportar a Excel ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_final.to_excel(writer, index=False, sheet_name="Ingresos_Egresos")

        workbook = writer.book
        worksheet = writer.sheets["Ingresos_Egresos"]
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'align': 'center'})
        money_format = workbook.add_format({'num_format': '$#,##0.00', 'align': 'right'})

        worksheet.set_row(0, None, header_format)
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:E', 20, money_format)
        worksheet.set_h_pagebreaks([])
        worksheet.set_v_pagebreaks([])

    st.download_button(
        label="💾 Descargar tabla Ingresos-Egresos (Excel)",
        data=output.getvalue(),
        file_name="Ingresos_Egresos_InfoManual.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def tabla_balance_acumulado():
    st.write("📊 **BALANCE GENERAL ACUMULADO")

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
                df_mapeo[[col_cuenta_mapeo, "CLASIFICACION", "CATEGORIA"]],
                left_on=col_cuenta_balance,
                right_on=col_cuenta_mapeo,
                how="left"
            )

            posibles_columnas_monto = ["Saldo Final"]
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

    # --- Inicializar columnas ---
    df_total["DEBE"] = 0.0
    df_total["HABER"] = 0.0
    df_total["MANUAL"] = 0.0

    # === Asignación automática base ===
    df_total.loc[df_total["CUENTA"].str.contains("CUENTAS POR COBRAR NO FACTURADAS", case=False), "DEBE"] = df_total["ACUMULADO"]
    df_total.loc[df_total["CUENTA"].str.contains("DEUDORES RELACIONADOS", case=False), "HABER"] = df_total["ACUMULADO"]
    df_total.loc[df_total["CUENTA"].str.contains("IVA ACREDITABLE", case=False), "HABER"] = df_total["ACUMULADO"]

    activo_imp_dif = df_total.loc[
        (df_total["CLASIFICACION"] == "ACTIVO") &
        (df_total["CUENTA"].str.contains("IMPUESTOS DIFERIDOS", case=False)),
        "ACUMULADO"
    ].sum()
    df_total.loc[
        (df_total["CLASIFICACION"] == "PASIVO") &
        (df_total["CUENTA"].str.contains("IMPUESTOS DIFERIDOS", case=False)),
        "DEBE"
    ] = activo_imp_dif

    iva_acred = df_total.loc[
        df_total["CUENTA"].str.contains("IVA ACREDITABLE", case=False),
        "ACUMULADO"
    ].sum()
    df_total.loc[df_total["CUENTA"].str.contains("IVA POR TRASLADAR", case=False), "DEBE"] = iva_acred

    deud_rel = df_total.loc[
        df_total["CUENTA"].str.contains("DEUDORES RELACIONADOS", case=False),
        "ACUMULADO"
    ].sum()
    df_total.loc[df_total["CUENTA"].str.contains("ACREEDORES RELACIONADOS", case=False), "DEBE"] = deud_rel * -1

    # === Crear estructura jerárquica (ACTIVO / PASIVO / CAPITAL) ===
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

    # === Reemplazar vacíos por 0 para edición ===
    for col in ["DEBE", "HABER", "MANUAL"]:
        df_final[col] = pd.to_numeric(df_final[col], errors="coerce").fillna(0.0)

    # === Cálculo inicial de TOTALES ===
    df_final["TOTALES"] = (
        df_final["ACUMULADO"].replace("", 0).astype(float)
        + df_final["DEBE"].astype(float)
        - df_final["HABER"].astype(float)
        + df_final["MANUAL"].astype(float)
    )

    # === Editor interactivo ===
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

    # === Recalcular TOTALES tras edición ===
    for col in ["DEBE", "HABER", "MANUAL"]:
        df_editable[col] = pd.to_numeric(df_editable[col], errors="coerce").fillna(0.0)

    df_editable["TOTALES"] = (
        df_editable["ACUMULADO"].replace("", 0).astype(float)
        + df_editable["DEBE"].astype(float)
        - df_editable["HABER"].astype(float)
        + df_editable["MANUAL"].astype(float)
    )

    # === Mostrar tabla final ===
    st.markdown("### 📊 **Balance Final Recalculado:**")
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

    # === Validación contable ===
    total_activo = df_editable.loc[df_editable["CUENTA"] == "TOTAL ACTIVO", "TOTALES"].sum()
    total_pasivo = df_editable.loc[df_editable["CUENTA"] == "TOTAL PASIVO", "TOTALES"].sum()
    total_capital = df_editable.loc[df_editable["CUENTA"] == "TOTAL CAPITAL", "TOTALES"].sum()
    balance = total_activo - (total_pasivo + total_capital)

    st.markdown("### ⚖️ **Validación del Balance General**")
    st.write(f"**Total Activo:** ${total_activo:,.2f}")
    st.write(f"**Total Pasivo:** ${total_pasivo:,.2f}")
    st.write(f"**Total Capital:** ${total_capital:,.2f}")
    st.write(f"**Balance (Activo - Pasivo - Capital):** ${balance:,.2f}")

    if abs(balance) < 1:
        st.success("✅ El balance general está cuadrado (ACTIVO = PASIVO + CAPITAL).")
    else:
        st.error("❌ El balance no cuadra. Revisa los montos.")

    # === Descargar en Excel ===
    st.markdown("### 💾 **Descargar Balance en Excel**")

    def convertir_a_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Balance_Recalculado")

            # 🔹 Quitar líneas de salto de página
            workbook = writer.book
            worksheet = writer.sheets["Balance_Recalculado"]
            worksheet.set_h_pagebreaks([])
            worksheet.set_v_pagebreaks([])
            worksheet.fit_to_pages(1, 0)

        return output.getvalue()

    excel_data = convertir_a_excel(df_editable)

    st.download_button(
        label="📥 Descargar Balance Recalculado (.xlsx)",
        data=excel_data,
        file_name="Balance_Recalculado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

if selected == "BALANCE POR EMPRESA":
    tabla_balance_por_empresa()

elif selected == "BALANCE GENERAL ACUMULADO":
    tabla_balance_acumulado()
    tabla_Ingresos_Egresos()

    tabla_ingresos_egresos2()
