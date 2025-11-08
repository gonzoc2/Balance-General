import pandas as pd
import streamlit as st
import requests
from io import BytesIO
from functools import reduce
from streamlit_option_menu import option_menu
import numpy as np

st.markdown("### 🔄 Actualizar información")

if st.button("♻️ Recargar datos"):
    st.cache_data.clear()

# --- Cargar datos desde secrets ---
balance_url = st.secrets["urls"]["balance_url"]
mapeo_url = st.secrets["urls"]["mapeo_url"]
info_manual = st.secrets["urls"]["info_manual"]

@st.cache_data
def load_data(url):
    return pd.read_excel(url)

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

# ---------------------------------------------------------------------
# 🔹 BALANCE POR EMPRESA
# ---------------------------------------------------------------------
if selected == "BALANCE POR EMPRESA":

    def tabla_balance_por_empresa():
        st.subheader("📘 Balance General por Empresa (referencia por 'Cuenta' con auditoría de mapeo)")

        from functools import reduce
        import requests
        from io import BytesIO
        import xlsxwriter

        # --- Limpieza uniforme ---
        def limpiar_cuenta(x):
            try:
                return int(str(x).strip().replace(".0", ""))
            except:
                return pd.NA

        # --- Cargar y limpiar mapeo ---
        @st.cache_data(show_spinner="Cargando mapeo de cuentas...")
        def cargar_mapeo(url):
            r = requests.get(url)
            r.raise_for_status()
            file = BytesIO(r.content)
            df_mapeo = pd.read_excel(file, engine="openpyxl")
            df_mapeo.columns = df_mapeo.columns.str.strip()

            if "Cuenta" not in df_mapeo.columns:
                st.error("❌ La hoja de mapeo debe contener una columna llamada 'Cuenta'.")
                return pd.DataFrame()

            df_mapeo["Cuenta"] = df_mapeo["Cuenta"].apply(limpiar_cuenta)
            df_mapeo = (
                df_mapeo.dropna(subset=["Cuenta"])
                        .drop_duplicates(subset=["Cuenta"], keep="first")
            )
            return df_mapeo

        # --- Cargar balances ---
        @st.cache_data(show_spinner="Cargando hojas del balance...")
        def cargar_balance(url, hojas):
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

        # --- Configuración general ---
        hojas_empresas = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]
        df_mapeo = cargar_mapeo(mapeo_url)
        data_empresas = cargar_balance(balance_url, hojas_empresas)

        posibles_columnas_cuenta = ["Cuenta", "Código", "No. Cuenta"]
        posibles_columnas_monto = ["Saldo final", "Saldo", "Monto", "Importe", "Valor"]

        resultados = []
        balances_detallados = {}
        cuentas_no_mapeadas = []

        for empresa in hojas_empresas:
            if empresa not in data_empresas:
                continue

            df = data_empresas[empresa].copy()
            col_cuenta = next((c for c in posibles_columnas_cuenta if c in df.columns), None)
            col_monto = next((c for c in posibles_columnas_monto if c in df.columns), None)

            if not col_cuenta or not col_monto:
                st.warning(f"⚠️ {empresa}: columnas inválidas ('Cuenta' / 'Saldo').")
                continue

            df[col_cuenta] = df[col_cuenta].apply(limpiar_cuenta)
            df[col_monto] = (
                df[col_monto]
                .replace("[\$,]", "", regex=True)
                .replace(",", "", regex=True)
            )
            df[col_monto] = pd.to_numeric(df[col_monto], errors="coerce").fillna(0)

            # 🔹 Agrupar duplicadas
            df = df.groupby(col_cuenta, as_index=False)[col_monto].sum()

            # --- Auditoría: cuentas que no existen en el mapeo ---
            cuentas_no_en_mapeo = df.loc[~df[col_cuenta].isin(df_mapeo["Cuenta"])]
            if not cuentas_no_en_mapeo.empty:
                cuentas_no_en_mapeo["EMPRESA"] = empresa
                cuentas_no_mapeadas.append(cuentas_no_en_mapeo)

            # --- Merge exacto ---
            df_merged = df.merge(
                df_mapeo[["Cuenta", "CLASIFICACION", "CATEGORIA"]],
                on="Cuenta",
                how="inner"
            )

            if df_merged.empty:
                st.warning(f"⚠️ {empresa}: sin coincidencias exactas con el mapeo.")
                continue

            resumen = (
                df_merged.groupby(["CLASIFICACION", "CATEGORIA"])[col_monto]
                .sum()
                .reset_index()
                .rename(columns={col_monto: empresa})
            )
            resultados.append(resumen)
            balances_detallados[empresa] = df_merged.copy()

        # === Si no hay datos ===
        if not resultados:
            st.error("❌ No se pudo generar información consolidada.")
            return

        # --- Consolidado ---
        df_final = reduce(
            lambda l, r: pd.merge(l, r, on=["CLASIFICACION", "CATEGORIA"], how="outer"),
            resultados
        ).fillna(0)
        df_final["TOTAL ACUMULADO"] = df_final[hojas_empresas].sum(axis=1)

        # --- Mostrar por clasificación ---
        for clasif in ["ACTIVO", "PASIVO", "CAPITAL"]:
            st.markdown(f"### 🔹 {clasif}")
            df_clasif = df_final[df_final["CLASIFICACION"] == clasif].copy()
            if df_clasif.empty:
                st.info(f"No hay cuentas clasificadas como {clasif}.")
                continue

            subtotal = pd.DataFrame({
                "CLASIFICACION": [clasif],
                "CATEGORIA": [f"TOTAL {clasif}"]
            })
            for col in hojas_empresas + ["TOTAL ACUMULADO"]:
                subtotal[col] = df_clasif[col].sum()
            df_clasif = pd.concat([df_clasif, subtotal], ignore_index=True)

            for col in hojas_empresas + ["TOTAL ACUMULADO"]:
                df_clasif[col] = df_clasif[col].apply(lambda x: f"${x:,.2f}")

            with st.expander(f"📘 {clasif} (detalle de cuentas)"):
                st.dataframe(df_clasif.drop(columns=["CLASIFICACION"]), use_container_width=True, hide_index=True)

                # --- Detalle por empresa ---
                for empresa in hojas_empresas:
                    if empresa in balances_detallados:
                        df_detalle = balances_detallados[empresa]
                        df_detalle = df_detalle[df_detalle["CLASIFICACION"] == clasif]
                        if not df_detalle.empty:
                            st.markdown(f"**{empresa} — detalle de cuentas:**")
                            st.dataframe(
                                df_detalle[["CATEGORIA", "Cuenta", col_monto]].style.format({col_monto: "${:,.2f}"}),
                                use_container_width=True,
                                hide_index=True
                            )

        # --- Resumen final ---
        totales = {
            "ACTIVO": df_final[df_final["CLASIFICACION"] == "ACTIVO"]["TOTAL ACUMULADO"].sum(),
            "PASIVO": df_final[df_final["CLASIFICACION"] == "PASIVO"]["TOTAL ACUMULADO"].sum(),
            "CAPITAL": df_final[df_final["CLASIFICACION"] == "CAPITAL"]["TOTAL ACUMULADO"].sum(),
        }
        diferencia = totales["ACTIVO"] + (totales["PASIVO"] + totales["CAPITAL"])

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

        if abs(diferencia) < 1:
            st.success("✅ El balance está cuadrado (ACTIVO = PASIVO + CAPITAL).")
        else:
            st.error("❌ El balance no cuadra. Revisa las cuentas listadas en los expanders.")

        # =======================================================
        # 🚨 AUDITORÍA DE CUENTAS NO MAPEADAS
        # =======================================================
        if cuentas_no_mapeadas:
            df_no_mapeadas = pd.concat(cuentas_no_mapeadas, ignore_index=True)
            df_no_mapeadas = df_no_mapeadas.sort_values(["EMPRESA", col_cuenta])
            with st.expander("⚠️ Cuentas no mapeadas (revisar en catálogo)", expanded=False):
                st.warning("Estas cuentas existen en los balances pero no en el mapeo.")
                st.dataframe(
                    df_no_mapeadas[["EMPRESA", col_cuenta, col_monto]].style.format({col_monto: "${:,.2f}"}),
                    use_container_width=True,
                    hide_index=True
                )
            # Descarga de auditoría
            output_audit = BytesIO()
            with pd.ExcelWriter(output_audit, engine="xlsxwriter") as writer:
                df_no_mapeadas.to_excel(writer, index=False, sheet_name="Cuentas_NoMapeadas")
            st.download_button(
                label="📥 Descargar cuentas no mapeadas",
                data=output_audit.getvalue(),
                file_name="Cuentas_NoMapeadas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            for empresa, df_emp in balances_detallados.items():
                df_emp.to_excel(writer, index=False, sheet_name=empresa)
                ws = writer.sheets[empresa]
                ws.set_column("A:A", 20)
                ws.set_column("B:B", 40)
                ws.set_column("C:D", 20)

            df_final.to_excel(writer, index=False, sheet_name="Consolidado")
            resumen_final.to_excel(writer, index=False, sheet_name="Resumen")

            writer.sheets["Consolidado"].set_column("A:B", 25)
            writer.sheets["Resumen"].set_column("A:B", 25)

        st.download_button(
            label="💾 Descargar Excel Consolidado (por Cuenta)",
            data=output.getvalue(),
            file_name="Balance_PorCuenta_ConAuditoria.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    tabla_balance_por_empresa()

# ---------------------------------------------------------------------
# 🔹 BALANCE GENERAL ACUMULADO
# ---------------------------------------------------------------------
elif selected == "BALANCE GENERAL ACUMULADO":
    st.subheader("📘 Balance General Acumulado (con base en Balance por Empresa)")

    from io import BytesIO
    import requests
    from functools import reduce

    # =====================================================
    # 1️⃣ Cargar el TOTAL ACUMULADO del Balance por Empresa
    # =====================================================
    @st.cache_data(show_spinner="Cargando balance general acumulado...")
    def get_total_acumulado(balance_url, mapeo_url):
        hojas_empresas = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]

        # --- Leer archivos ---
        r_map = requests.get(mapeo_url)
        df_mapeo = pd.read_excel(BytesIO(r_map.content), engine="openpyxl")
        df_mapeo.columns = df_mapeo.columns.str.strip()
        if "Cuenta" not in df_mapeo.columns:
            posibles = ["Descripción", "Concepto"]
            col_cuenta = next((c for c in posibles if c in df_mapeo.columns), None)
            if col_cuenta:
                df_mapeo = df_mapeo.rename(columns={col_cuenta: "Cuenta"})

        r_bal = requests.get(balance_url)
        file_bal = BytesIO(r_bal.content)
        data_empresas = {}
        for hoja in hojas_empresas:
            try:
                df = pd.read_excel(file_bal, sheet_name=hoja, engine="openpyxl")
                data_empresas[hoja] = df
            except Exception:
                continue

        # --- Generar totales por CLASIFICACION / CATEGORIA ---
        resultados = []
        for hoja, df in data_empresas.items():
            if "Cuenta" not in df.columns:
                posibles = ["Descripción", "Concepto"]
                col_cuenta = next((c for c in posibles if c in df.columns), None)
                if col_cuenta:
                    df = df.rename(columns={col_cuenta: "Cuenta"})

            if "Saldo final" not in df.columns:
                continue

            df["Saldo final"] = pd.to_numeric(df["Saldo final"], errors="coerce").fillna(0)
            df = df.merge(df_mapeo[["Cuenta", "CLASIFICACION", "CATEGORIA"]],
                          on="Cuenta", how="left")
            resumen = (
                df.groupby(["CLASIFICACION", "CATEGORIA"])["Saldo final"]
                .sum()
                .reset_index()
                .rename(columns={"Saldo final": hoja})
            )
            resultados.append(resumen)

        df_final = reduce(lambda l, r: pd.merge(l, r, on=["CLASIFICACION", "CATEGORIA"], how="outer"),
                          resultados).fillna(0)
        df_final["TOTAL ACUMULADO"] = df_final[hojas_empresas].sum(axis=1)
        return df_final, df_mapeo

    df_acumulado, df_mapeo = get_total_acumulado(balance_url, mapeo_url)

    # =====================================================
    # 2️⃣ TABLA DE INVERSIONES ENTRE COMPAÑÍAS
    # =====================================================
    st.markdown("### 💼 Inversiones entre Compañías")

    inversiones_dict = {
        "HDL-WH": "INVERSION ESGARI WAREHOUSING",
        "EHM-WH": "INVERSION ESGARI WAREHOUSING",
        "FWD-WH": "ACCIONES ESGARI WAREHOUSING & MANUFACTURING",
        "EHM-FWD": "INVERSION ESGARI FORWARDING",
        "EHM-UBIKARGA": "INVERSION UBIKARGA",
        "EHM-GREEN": "INVERSION ESGARI GREEN",
        "EHM-RESA": "INVERSION RESA MULTIMODAL",
        "EHM-HOLDING": "INVERSION ESGARI HOLDING"
    }

    df_inversiones = []
    xls_balance = pd.ExcelFile(balance_url)

    for clave, descripcion in inversiones_dict.items():
        hoja = clave.split("-")[0].replace("HDL", "HOLDING")
        if hoja not in xls_balance.sheet_names:
            continue

        df = pd.read_excel(xls_balance, sheet_name=hoja)
        posibles = ["Cuenta", "Descripción", "Concepto"]
        col_cuenta = next((c for c in posibles if c in df.columns), None)
        col_monto = "Saldo final" if "Saldo final" in df.columns else None
        if not col_cuenta or not col_monto:
            continue

        df[col_monto] = pd.to_numeric(df[col_monto], errors="coerce").fillna(0)
        df[col_cuenta] = df[col_cuenta].astype(str).str.upper().str.strip()

        monto = df.loc[df[col_cuenta].str.contains(descripcion.upper(), na=False), col_monto].sum()

        df_inversiones.append({
            "VARIABLE": clave,
            "CUENTA": descripcion,
            "ACTIVO": monto,
            "SOCIAL": 0.0,
            "TOTALES": monto
        })

    df_inv = pd.DataFrame(df_inversiones)
    if df_inv.empty:
        st.warning("⚠️ No se encontraron inversiones con las descripciones dadas.")
        total_activo = total_social = goodwill = 0
    else:
        # Ajustar capital social
        for i, row in df_inv.iterrows():
            if row["VARIABLE"] == "HDL-WH":
                df_inv.at[i, "SOCIAL"] = 14404988.06
            else:
                df_inv.at[i, "SOCIAL"] = row["ACTIVO"]
            df_inv.at[i, "TOTALES"] = row["ACTIVO"] - df_inv.at[i, "SOCIAL"]

        total_activo = df_inv["ACTIVO"].sum()
        total_social = df_inv["SOCIAL"].sum()
        goodwill = (total_activo + total_social) * -1

        df_inv = pd.concat([
            df_inv,
            pd.DataFrame([{
                "VARIABLE": "",
                "CUENTA": "EHM HOLDING GOODWILL (Intangibles)",
                "ACTIVO": goodwill,
                "SOCIAL": 0,
                "TOTALES": goodwill
            }])
        ], ignore_index=True)

        st.dataframe(df_inv.style.format({
            "ACTIVO": "${:,.2f}",
            "SOCIAL": "${:,.2f}",
            "TOTALES": "${:,.2f}",
        }), use_container_width=True, hide_index=True)

    # =====================================================
    # 3️⃣ BALANCE GENERAL ACUMULADO FINAL (Editable persistente)
    # =====================================================
    st.markdown("### 📊 Balance General Acumulado (Editable y Persistente)")

    # --- Botón para limpiar solo los valores manuales ---
    if st.button("🔄 Recargar manuales"):
        if "manual_values" in st.session_state:
            del st.session_state["manual_values"]
        st.success("✅ Se reiniciaron los valores manuales correctamente.")
        st.experimental_rerun()

    df_total = df_acumulado.copy()
    df_total["ACUMULADO"] = df_total["TOTAL ACUMULADO"]

    df_total["DEBE"] = 0.0
    df_total["HABER"] = 0.0
    df_total["MANUAL"] = 0.0

    df_total.loc[
        df_total["CATEGORIA"].str.contains("GOODWILL", case=False, na=False), "DEBE"
    ] = goodwill
    total_capital_social = total_social + total_activo
    df_total.loc[
        df_total["CATEGORIA"].str.contains("CAPITAL SOCIAL", case=False, na=False), "DEBE"
    ] = total_capital_social

    df_total["TOTALES"] = df_total["ACUMULADO"] + df_total["DEBE"] - df_total["HABER"] + df_total["MANUAL"]
    df_total = df_total.rename(columns={"CATEGORIA": "CUENTA"})
    columnas_visibles = ["CLASIFICACION", "CUENTA", "ACUMULADO", "DEBE", "HABER", "MANUAL", "TOTALES"]
    df_total = df_total[columnas_visibles]

    # --- Mantener valores manuales entre cambios de pestaña ---
    if "manual_values" not in st.session_state:
        st.session_state.manual_values = df_total["MANUAL"].tolist()

    df_total["MANUAL"] = st.session_state.manual_values

    st.markdown("📝 **Puedes editar la columna 'MANUAL' (se mantiene hasta recargar o usar el botón de arriba):**")

    df_editable = st.data_editor(
        df_total,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "ACUMULADO": st.column_config.NumberColumn(format="$%.2f", disabled=True),
            "DEBE": st.column_config.NumberColumn(format="$%.2f", disabled=True),
            "HABER": st.column_config.NumberColumn(format="$%.2f", disabled=True),
            "MANUAL": st.column_config.NumberColumn(format="$%.2f", help="Ajuste manual editable"),
            "TOTALES": st.column_config.NumberColumn(format="$%.2f", disabled=True),
            "CUENTA": st.column_config.TextColumn(width="large", disabled=True),
            "CLASIFICACION": st.column_config.TextColumn(width="small", disabled=True),
        },
        key="balance_editable",
    )

    # Guardar los cambios manuales
    st.session_state.manual_values = df_editable["MANUAL"].tolist()

    # Recalcular totales con los ajustes manuales
    df_editable["TOTALES"] = (
        df_editable["ACUMULADO"]
        + df_editable["DEBE"]
        - df_editable["HABER"]
        + df_editable["MANUAL"]
    )

    st.markdown("### ✅ Balance con ajustes manuales aplicados")
    st.dataframe(
        df_editable.style.format({
            "ACUMULADO": "${:,.2f}",
            "DEBE": "${:,.2f}",
            "HABER": "${:,.2f}",
            "MANUAL": "${:,.2f}",
            "TOTALES": "${:,.2f}",
        }),
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # 4️⃣ INGRESOS / EGRESOS
    # =====================================================
    st.markdown("### 💰 Ingresos y Gastos Consolidados")

    df_ige = df_acumulado[df_acumulado["CLASIFICACION"].isin(["INGRESO", "GASTOS"])].copy()
    if df_ige.empty:
        st.info("No se encontraron ingresos ni gastos en el mapeo.")
    else:
        resumen_ie = (
            df_ige.groupby("CLASIFICACION")["TOTAL ACUMULADO"]
            .sum()
            .reset_index()
            .rename(columns={"TOTAL ACUMULADO": "MONTO"})
        )
        ingreso = resumen_ie.loc[resumen_ie["CLASIFICACION"] == "INGRESO", "MONTO"].sum()
        gasto = resumen_ie.loc[resumen_ie["CLASIFICACION"] == "GASTOS", "MONTO"].sum()
        utilidad = ingreso - gasto

        df_resumen_ie = pd.DataFrame({
            "Concepto": ["Ingresos", "Gastos", "Utilidad del Ejercicio"],
            "Monto": [ingreso, gasto, utilidad]
        })
        st.dataframe(df_resumen_ie.style.format({"Monto": "${:,.2f}"}),
                     use_container_width=True, hide_index=True)


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


























