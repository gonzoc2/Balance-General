import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from io import BytesIO
import requests
from functools import reduce
import xlsxwriter

st.set_page_config(
    page_title="Esgari 360",
    page_icon="🚚",  # <- icono de camión
    layout="wide"    # <- modo pantalla completa
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

EMPRESAS = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]

COLUMNAS_CUENTA = ["Cuenta", "Código", "No. Cuenta", "Descripción", "Concepto", "Nombre de la cuenta"]
COLUMNAS_MONTO = ["Saldo final", "Saldo", "Monto", "Importe", "Valor"]
CLASIFICACIONES_PRINCIPALES = ["ACTIVO", "PASIVO", "CAPITAL"]
CLASIFICACIONES_RESULTADOS = ["INGRESO", "GASTOS"]
DEF_BALANCE_FINAL = pd.DataFrame()


st.markdown("### 🔄 Actualizar información")
if st.button("♻️ Recargar datos"):
    st.cache_data.clear()

# --- Cargar datos desde secrets ---
balance_url = st.secrets["urls"]["balance_url"]
mapeo_url = st.secrets["urls"]["mapeo_url"]
info_manual = st.secrets["urls"]["info_manual"]

@st.cache_data
def load_data(url):
    """Carga datos desde una URL Excel"""
    return pd.read_excel(url)

@st.cache_data(show_spinner="Cargando mapeo de cuentas...")
def cargar_mapeo(url):
    """Carga el archivo de mapeo y limpia la columna Cuenta"""
    r = requests.get(url)
    r.raise_for_status()
    file = BytesIO(r.content)
    df_mapeo = pd.read_excel(file, engine="openpyxl")
    df_mapeo.columns = df_mapeo.columns.str.strip()
    if "Cuenta" not in df_mapeo.columns:
        st.error("❌ La hoja de mapeo debe contener una columna llamada 'Cuenta'.")
        return pd.DataFrame()
    df_mapeo["Cuenta"] = df_mapeo["Cuenta"].apply(limpiar_cuenta)
    df_mapeo = df_mapeo.dropna(subset=["Cuenta"]).drop_duplicates(subset=["Cuenta"], keep="first")
    return df_mapeo

@st.cache_data(show_spinner="Cargando hojas del balance...")
def cargar_balance(url, hojas):
    """Carga múltiples hojas desde el balance general"""
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

def limpiar_cuenta(x):
    """Limpia valores numéricos de la columna 'Cuenta'"""
    try:
        return int(str(x).strip().replace(".0", ""))
    except:
        return pd.NA

# =========================================================
# 🔸 CARGA INICIAL
# =========================================================
df_balance = load_data(balance_url)
df_mapeo = load_data(mapeo_url)
df_info = load_data(info_manual)

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

# =========================================================
# 🔹 BALANCE POR EMPRESA
# =========================================================
if selected == "BALANCE POR EMPRESA":

    def tabla_balance_por_empresa():
        st.subheader("📘 Balance General por Empresa (referencia por 'Cuenta' con auditoría extendida)")

        df_mapeo_local = cargar_mapeo(mapeo_url)
        data_empresas = cargar_balance(balance_url, EMPRESAS)

        resultados = []
        balances_detallados = {}
        cuentas_no_mapeadas = []
        resumen_ingresos_egresos = []

        for empresa in EMPRESAS:
            if empresa not in data_empresas:
                continue

            df = data_empresas[empresa].copy()
            col_cuenta = next((c for c in COLUMNAS_CUENTA if c in df.columns), None)
            col_monto = next((c for c in COLUMNAS_MONTO if c in df.columns), None)

            if not col_cuenta or not col_monto:
                st.warning(f"⚠️ {empresa}: columnas inválidas ('Cuenta' / 'Saldo').")
                continue

            df[col_cuenta] = df[col_cuenta].apply(limpiar_cuenta)
            df[col_monto] = (
                df[col_monto].replace("[\$,]", "", regex=True)
                             .replace(",", "", regex=True)
            )
            df[col_monto] = pd.to_numeric(df[col_monto], errors="coerce").fillna(0)

            # --- Agrupar duplicadas ---
            df = df.groupby(col_cuenta, as_index=False)[col_monto].sum()

            # --- Auditoría: cuentas no mapeadas ---
            df_no_mapeadas = df.loc[~df[col_cuenta].isin(df_mapeo_local["Cuenta"])].copy()
            if not df_no_mapeadas.empty:
                df_no_mapeadas["EMPRESA"] = empresa

                # Clasificación automática
                df_no_mapeadas["CLASIFICACION_AUTO"] = df_no_mapeadas[col_monto].apply(
                    lambda x: "INGRESO (>400M)" if x > 400_000_000
                    else ("EGRESO (>500M)" if x > 500_000_000 else "")
                )

                # --- Filtrar las relevantes ---
                df_filtradas = df_no_mapeadas[
                    (df_no_mapeadas["CLASIFICACION_AUTO"] != "")
                ].copy()

                if not df_filtradas.empty:
                    resumen_ingresos_egresos.append(df_filtradas)

                cuentas_no_mapeadas.append(df_no_mapeadas)

            # --- Merge con mapeo ---
            df_merged = df.merge(
                df_mapeo_local[["Cuenta", "CLASIFICACION", "CATEGORIA"]],
                on="Cuenta", how="inner"
            )
            if df_merged.empty:
                st.warning(f"⚠️ {empresa}: sin coincidencias exactas con el mapeo.")
                continue

            resumen = (
                df_merged.groupby(["CLASIFICACION", "CATEGORIA"])[col_monto]
                .sum().reset_index().rename(columns={col_monto: empresa})
            )
            resultados.append(resumen)
            balances_detallados[empresa] = df_merged.copy()

        # --- Consolidar balances ---
        if not resultados:
            st.error("❌ No se pudo generar información consolidada.")
            return

        df_final = reduce(
            lambda l, r: pd.merge(l, r, on=["CLASIFICACION", "CATEGORIA"], how="outer"),
            resultados
        ).fillna(0)
        df_final["TOTAL ACUMULADO"] = df_final[EMPRESAS].sum(axis=1)

        # --- Mostrar balance principal ---
        for clasif in CLASIFICACIONES_PRINCIPALES:
            st.markdown(f"### 🔹 {clasif}")
            df_clasif = df_final[df_final["CLASIFICACION"] == clasif].copy()
            if df_clasif.empty:
                st.info(f"No hay cuentas clasificadas como {clasif}.")
                continue

            subtotal = pd.DataFrame({
                "CLASIFICACION": [clasif],
                "CATEGORIA": [f"TOTAL {clasif}"]
            })
            for col in EMPRESAS + ["TOTAL ACUMULADO"]:
                subtotal[col] = df_clasif[col].sum()
            df_clasif = pd.concat([df_clasif, subtotal], ignore_index=True)

            for col in EMPRESAS + ["TOTAL ACUMULADO"]:
                df_clasif[col] = df_clasif[col].apply(lambda x: f"${x:,.2f}")

            with st.expander(f"📘 {clasif} (detalle de cuentas)"):
                st.dataframe(
                    df_clasif.drop(columns=["CLASIFICACION"]),
                    use_container_width=True,
                    hide_index=True
                )

        # --- Resumen total ---
        totales = {
            c: df_final[df_final["CLASIFICACION"] == c]["TOTAL ACUMULADO"].sum()
            for c in CLASIFICACIONES_PRINCIPALES
        }
        diferencia = totales["ACTIVO"] - (totales["PASIVO"] + totales["CAPITAL"])

        resumen_final = pd.DataFrame({
            "Concepto": ["TOTAL ACTIVO", "TOTAL PASIVO", "TOTAL CAPITAL", "DIFERENCIA (Debe ser 0)"],
            "Monto Total": [
                f"${totales['ACTIVO']:,.2f}",
                f"${totales['PASIVO']:,.2f}",
                f"${totales['CAPITAL']:,.2f}",
                f"${diferencia:,.2f}"
            ]
        })
        st.markdown("### 📊 Resumen Consolidado")
        st.dataframe(resumen_final, use_container_width=True, hide_index=True)

        # --- Estado del balance ---
        if abs(diferencia) < 1:
            st.success("✅ El balance está cuadrado (ACTIVO = PASIVO + CAPITAL).")
        else:
            st.error("❌ El balance no cuadra. Revisa las cuentas listadas.")

        # =========================================================
        # 🚨 CUENTAS NO MAPEADAS Y RESUMEN INGRESOS/EGRESOS
        # =========================================================
        if cuentas_no_mapeadas:
            df_no_mapeadas = pd.concat(cuentas_no_mapeadas, ignore_index=True)
            df_no_mapeadas = df_no_mapeadas.sort_values(["EMPRESA", col_cuenta])
            st.markdown("### ⚠️ Cuentas no mapeadas")
            st.dataframe(
                df_no_mapeadas[["EMPRESA", col_cuenta, col_monto]]
                .style.format({col_monto: "${:,.2f}"}),
                use_container_width=True,
                hide_index=True
            )

        if resumen_ingresos_egresos:
            df_resumen_ie = pd.concat(resumen_ingresos_egresos, ignore_index=True)
            df_resumen_ie = df_resumen_ie.sort_values(["EMPRESA", "CLASIFICACION_AUTO", col_monto], ascending=[True, False, False])
            st.markdown("### 💰 Cuentas no mapeadas mayores a umbrales (clasificadas)")
            st.dataframe(
                df_resumen_ie[["EMPRESA", col_cuenta, col_monto, "CLASIFICACION_AUTO"]]
                .style.format({col_monto: "${:,.2f}"}),
                use_container_width=True,
                hide_index=True
            )

            # --- Descargar auditoría extendida ---
            output_audit = BytesIO()
            with pd.ExcelWriter(output_audit, engine="xlsxwriter") as writer:
                df_no_mapeadas.to_excel(writer, index=False, sheet_name="Cuentas_NoMapeadas")
                df_resumen_ie.to_excel(writer, index=False, sheet_name="Mayores_Clasificados")
            st.download_button(
                label="📥 Descargar auditoría extendida (Excel)",
                data=output_audit.getvalue(),
                file_name="Cuentas_NoMapeadas_y_Clasificadas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # =========================================================
        # 💾 DESCARGA CONSOLIDADO PRINCIPAL
        # =========================================================
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            for empresa, df_emp in balances_detallados.items():
                df_emp.to_excel(writer, index=False, sheet_name=empresa)
            df_final.to_excel(writer, index=False, sheet_name="Consolidado")
            resumen_final.to_excel(writer, index=False, sheet_name="Resumen")
        st.download_button(
            label="💾 Descargar Excel Consolidado (por Cuenta)",
            data=output.getvalue(),
            file_name="Balance_PorCuenta_ConAuditoria.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    tabla_balance_por_empresa()


elif selected == "BALANCE GENERAL ACUMULADO":
    st.markdown("### 🔄 Control manual de edición")
    if st.button("♻️ Recargar manuales"):
        st.session_state.pop("df_balance_manual", None)
        st.success("✅ Datos manuales recargados correctamente.")
    # =====================================================
    # 1️⃣ TABLA DE INVERSIONES ENTRE COMPAÑÍAS
    # =====================================================
    def tabla_inversiones(balance_url, df_mapeo):
        st.subheader("📊 Inversiones entre Compañías (Activos)")

        inversiones_dict = {
            "HDL-WH": {"hoja": "HOLDING", "Descripción": "INVERSION ESGARI WAREHOUSING"},
            "EHM-WH": {"hoja": "EHM", "Descripción": "INVERSION ESGARI WAREHOUSING"},
            "FWD-WH": {"hoja": "FWD", "Descripción": "ACCIONES ESGARI WAREHOUSING & MANUFACTURING"},
            "EHM-FWD": {"hoja": "EHM", "Descripción": "INVERSION ESGARI FORWARDING"},
            "EHM-UBIKARGA": {"hoja": "EHM", "Descripción": "INVERSION UBIKARGA"},
            "EHM-GREEN": {"hoja": "EHM", "Descripción": "INVERSION ESGARI GREEN"},
            "EHM-RESA": {"hoja": "EHM", "Descripción": "INVERSION RESA MULTIMODAL"},
            "EHM-HOLDING": {"hoja": "EHM", "Descripción": "INVERSION ESGARI HOLDING"},
        }

        try:
            xls_balance = pd.ExcelFile(balance_url)
        except Exception as e:
            st.error(f"❌ Error al leer el archivo del balance: {e}")
            return 0, 0, 0

        data_inversiones = []

        for clave, info in inversiones_dict.items():
            hoja, descripcion = info["hoja"], info["Descripción"]
            if hoja not in xls_balance.sheet_names:
                continue

            df = pd.read_excel(xls_balance, sheet_name=hoja)
            if "Descripción" not in df.columns:
                posibles = [c for c in COLUMNAS_CUENTA if c in df.columns]
                col_cuenta = posibles[0] if posibles else None
                if col_cuenta:
                    df = df.rename(columns={col_cuenta: "Descripción"})

            col_monto = next((c for c in COLUMNAS_MONTO if c in df.columns), None)
            if not col_monto:
                continue

            df[col_monto] = pd.to_numeric(df[col_monto], errors="coerce").fillna(0)
            df["Descripción"] = df["Descripción"].astype(str).str.strip().str.upper()

            mask = df["Descripción"].str.contains(descripcion.upper(), na=False)
            monto = df.loc[mask, col_monto].sum()

            data_inversiones.append({
                "VARIABLE": clave,
                "CUENTA": descripcion,
                "ACTIVO": monto,
                "SOCIAL": 0.0,
                "TOTALES": monto
            })

        if not data_inversiones:
            st.warning("⚠️ No se encontraron inversiones con las descripciones indicadas.")
            return 0, 0, 0

        df_inv = pd.DataFrame(data_inversiones)

        # Ajustes de capital social
        for i, row in df_inv.iterrows():
            if row["VARIABLE"] == "HDL-WH":
                df_inv.at[i, "SOCIAL"] = 14404988.06
            else:
                df_inv.at[i, "SOCIAL"] = row["ACTIVO"]

            df_inv.at[i, "TOTALES"] = row["ACTIVO"] - df_inv.at[i, "SOCIAL"]

        total_activo = df_inv["ACTIVO"].sum()
        total_social = df_inv["SOCIAL"].sum()
        GOODWILL = (total_activo + total_social) * -1

        df_inv = pd.concat([
            df_inv,
            pd.DataFrame([{
                "VARIABLE": "",
                "CUENTA": "EHM HOLDING GOODWILL (Intangibles)",
                "ACTIVO": GOODWILL,
                "SOCIAL": 0,
                "TOTALES": GOODWILL
            }])
        ], ignore_index=True)

        st.dataframe(
            df_inv.style.format({
                "ACTIVO": "${:,.2f}",
                "SOCIAL": "${:,.2f}",
                "TOTALES": "${:,.2f}",
            }),
            use_container_width=True,
            hide_index=True
        )

        return total_activo, total_social, GOODWILL


    # =====================================================
    # 2️⃣ TABLA DE BALANCE GENERAL ACUMULADO
    # =====================================================
 
    def tabla_balance_acumulado(total_social, total_inversiones, GOODWILL, balance_url, df_mapeo):
        st.subheader("📘 Balance General Acumulado")

        iva_por_pagar = 0.0  # puedes ajustar este valor global si lo deseas

        # --- Leer archivo Excel ---
        try:
            xls = pd.ExcelFile(balance_url)
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")
            return

        # --- Procesar hojas ---
        data_empresas = []
        for hoja in EMPRESAS:
            if hoja not in xls.sheet_names:
                continue

            df = pd.read_excel(xls, sheet_name=hoja)

            # --- Normalizar columna de cuenta ---
            if "Cuenta" not in df.columns:
                posibles = [c for c in COLUMNAS_CUENTA if c in df.columns]
                col_cuenta = posibles[0] if posibles else None
                if col_cuenta:
                    df = df.rename(columns={col_cuenta: "Cuenta"})

            # --- Detectar columna de monto ---
            col_monto = next((c for c in COLUMNAS_MONTO if c in df.columns), None)
            if not col_monto:
                continue

            # --- Preparar dataframe ---
            df[col_monto] = pd.to_numeric(df[col_monto], errors="coerce").fillna(0)
            df_merged = df.merge(
                df_mapeo[["Cuenta", "CLASIFICACION", "CATEGORIA"]],
                on="Cuenta",
                how="left"
            )

            df_filtrado = df_merged[df_merged["CLASIFICACION"].isin(CLASIFICACIONES_PRINCIPALES)]
            resumen = (
                df_filtrado.groupby(["CLASIFICACION", "CATEGORIA"])[col_monto]
                .sum()
                .reset_index()
                .rename(columns={col_monto: hoja})
            )
            data_empresas.append(resumen)

        if not data_empresas:
            st.warning("⚠️ No se encontraron datos válidos.")
            return

        # --- Consolidar balances ---
        df_total = reduce(
            lambda left, right: pd.merge(left, right, on=["CLASIFICACION", "CATEGORIA"], how="outer"),
            data_empresas
        )
        df_total = df_total.fillna(0)
        df_total["ACUMULADO"] = df_total[
            [c for c in df_total.columns if c not in ["CLASIFICACION", "CATEGORIA"]]
        ].sum(axis=1)
        df_total = df_total.rename(columns={"CATEGORIA": "CUENTA"})

        # ==================================================
        # 💡 Ajustes automáticos de DEBE y HABER
        # ==================================================
        df_total["DEBE"] = 0.0
        df_total["HABER"] = 0.0
        df_total["MANUAL"] = 0.0

        # Cuentas por cobrar
        df_total.loc[
            df_total["CUENTA"].str.contains("CUENTAS POR COBRAR NO FACTURADAS", case=False),
            "DEBE"
        ] = df_total["ACUMULADO"]

        # Deudores / IVA acreditable → HABER
        df_total.loc[
            df_total["CUENTA"].str.contains("DEUDORES RELACIONADOS|IVA ACREDITABLE", case=False),
            "HABER"
        ] = df_total["ACUMULADO"]

        # Impuestos diferidos
        activo_imp_dif = df_total.loc[
            (df_total["CLASIFICACION"] == "ACTIVO")
            & (df_total["CUENTA"].str.contains("IMPUESTOS DIFERIDOS", case=False)),
            "HABER"
        ].sum()
        df_total.loc[
            (df_total["CLASIFICACION"] == "PASIVO")
            & (df_total["CUENTA"].str.contains("IMPUESTOS DIFERIDOS", case=False)),
            "DEBE"
        ] = activo_imp_dif

        # IVA trasladado
        iva_acred = df_total.loc[
            df_total["CUENTA"].str.contains("IVA ACREDITABLE", case=False),
            "ACUMULADO"
        ].sum()
        df_total.loc[
            df_total["CUENTA"].str.contains("IVA POR TRASLADAR", case=False),
            "DEBE"
        ] = iva_acred
        df_total.loc[
            df_total["CUENTA"].str.contains("IVA POR TRASLADAR", case=False),
            "HABER"
        ] = iva_por_pagar

        # Acreedores relacionados
        deud_rel = df_total.loc[
            df_total["CUENTA"].str.contains("DEUDORES RELACIONADOS", case=False),
            "ACUMULADO"
        ].sum()
        df_total.loc[
            df_total["CUENTA"].str.contains("ACREEDORES RELACIONADOS", case=False),
            "DEBE"
        ] = deud_rel * -1

        # Goodwill
        df_total.loc[
            df_total["CUENTA"].str.contains("GOODWILL", case=False),
            "DEBE"
        ] = GOODWILL

        # Capital social
        total_capital_social = total_social + total_inversiones
        df_total.loc[
            df_total["CUENTA"].str.contains("CAPITAL SOCIAL", case=False),
            "DEBE"
        ] = total_capital_social

        # ==================================================
        # 🧮 Calcular totales
        # ==================================================
        df_total["TOTALES"] = (
            df_total["ACUMULADO"]
            + df_total["DEBE"]
            - df_total["HABER"]
            + df_total["MANUAL"]
        )

        # ==================================================
        # 📝 Edición manual persistente
        # ==================================================
        if "df_balance_manual" not in st.session_state:
            st.session_state["df_balance_manual"] = df_total.copy()

        df_editado = st.data_editor(
            st.session_state["df_balance_manual"],
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            column_config={
                "MANUAL": st.column_config.NumberColumn(
                    "MANUAL (editable)",
                    help="Valor manual editable",
                    format="%.2f"
                ),
            },
            key="balance_acumulado_editor",
        )

        # Recalcular totales tras edición
        df_editado["TOTALES"] = (
            df_editado["ACUMULADO"]
            + df_editado["DEBE"]
            - df_editado["HABER"]
            + df_editado["MANUAL"]
        )

        st.session_state["df_balance_manual"] = df_editado

        # ==================================================
        # 💰 Mostrar tabla final
        # ==================================================
        st.dataframe(
            df_editado.style.format({
                "ACUMULADO": "${:,.2f}",
                "DEBE": "${:,.2f}",
                "HABER": "${:,.2f}",
                "MANUAL": "${:,.2f}",
                "TOTALES": "${:,.2f}",
            }),
            use_container_width=True,
            hide_index=True
        )

        st.info("🧩 Los valores manuales se guardan automáticamente y solo se recargan al presionar ♻️ Recargar manuales.")

        return df_editado


    # =====================================================
    # 3️⃣ TABLA DE INGRESOS / EGRESOS
    # =====================================================
    def tabla_ingresos_egresos(balance_url, df_mapeo):
        st.subheader("📊 Ingresos, Gastos y Utilidad del Ejercicio")

        try:
            xls = pd.ExcelFile(balance_url)
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")
            return

        data_empresas = []
        for hoja in EMPRESAS:
            if hoja not in xls.sheet_names:
                continue

            df = pd.read_excel(xls, sheet_name=hoja)
            if "Cuenta" not in df.columns:
                posibles = [c for c in COLUMNAS_CUENTA if c in df.columns]
                col_cuenta = posibles[0] if posibles else None
                if col_cuenta:
                    df = df.rename(columns={col_cuenta: "Cuenta"})

            col_monto = next((c for c in COLUMNAS_MONTO if c in df.columns), None)
            if not col_monto:
                continue

            df[col_monto] = pd.to_numeric(df[col_monto], errors="coerce").fillna(0)
            df_merged = df.merge(df_mapeo[["Cuenta", "CLASIFICACION", "CATEGORIA"]], on="Cuenta", how="left")
            df_filtrado = df_merged[df_merged["CLASIFICACION"].isin(CLASIFICACIONES_RESULTADOS)]

            resumen = df_filtrado.groupby("CLASIFICACION")[col_monto].sum().reset_index()
            ingreso = resumen.loc[resumen["CLASIFICACION"] == "INGRESO", col_monto].sum()
            gasto = resumen.loc[resumen["CLASIFICACION"] == "GASTOS", col_monto].sum()
            utilidad = ingreso - gasto

            data_empresas.append({
                "EMPRESA": hoja,
                "INGRESOS": ingreso,
                "GASTOS": gasto,
                "UTILIDAD": utilidad
            })

        df_final = pd.DataFrame(data_empresas)
        df_final["TOTAL"] = df_final[["INGRESOS", "GASTOS", "UTILIDAD"]].sum(axis=1)

        st.dataframe(
            df_final.style.format({
                "INGRESOS": "${:,.2f}",
                "GASTOS": "${:,.2f}",
                "UTILIDAD": "${:,.2f}",
                "TOTAL": "${:,.2f}",
            }),
            use_container_width=True,
            hide_index=True
        )

        return df_final


    # =====================================================
    # 🔄 EJECUCIÓN PRINCIPAL
    # =====================================================
    total_activo, total_social, GOODWILL = tabla_inversiones(balance_url, df_mapeo)
    df_balance = tabla_balance_acumulado(total_social, total_activo, GOODWILL, balance_url, df_mapeo)
    df_ingresos = tabla_ingresos_egresos(balance_url, df_mapeo)
# =========================================================


elif selected == "BALANCE FINAL":
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



























