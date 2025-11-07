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
        st.subheader("📘 Balance General por Empresa (usando un solo mapeo)")

        @st.cache_data(show_spinner="Cargando mapeo de cuentas...")
        def cargar_mapeo(url):
            r = requests.get(url)
            r.raise_for_status()
            file = BytesIO(r.content)
            df_mapeo = pd.read_excel(file, engine="openpyxl")
            df_mapeo.columns = df_mapeo.columns.str.strip()
            df_mapeo["Descripción"] = df_mapeo["Descripción"].apply(limpiar_texto)
            return df_mapeo

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

        # --- Archivos y hojas ---
        hojas_empresas = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]
        df_mapeo = cargar_mapeo(mapeo_url)
        data_empresas = cargar_balance(balance_url, hojas_empresas)

        # --- Posibles nombres de columnas ---
        posibles_columnas_cuenta = ["Descripción", "Cuenta", "Concepto"]
        posibles_columnas_monto = ["Saldo final", "Saldo", "Monto", "Importe", "Valor"]

        resultados = []

        for empresa in hojas_empresas:
            if empresa not in data_empresas:
                st.warning(f"⚠️ No se encontró la hoja '{empresa}' en el archivo de balance.")
                continue

            df = data_empresas[empresa].copy()

            col_cuenta = next((c for c in posibles_columnas_cuenta if c in df.columns), None)
            col_monto = next((c for c in posibles_columnas_monto if c in df.columns), None)

            if not col_cuenta or not col_monto:
                st.warning(f"⚠️ {empresa}: no se encontraron columnas válidas (Descripción / Saldo).")
                continue

            # --- Limpieza de texto ---
            df[col_cuenta] = df[col_cuenta].apply(limpiar_texto)
            df[col_monto] = (
                df[col_monto]
                .replace("[\$,]", "", regex=True)
                .replace(",", "", regex=True)
            )
            df[col_monto] = pd.to_numeric(df[col_monto], errors="coerce").fillna(0)

            # --- Merge con mapeo (solo una hoja de mapeo) ---
            df_merged = df.merge(
                df_mapeo[["Descripción", "CLASIFICACION", "CATEGORIA"]],
                on="Descripción",
                how="left"
            )

            # --- Agrupar y sumar ---
            resumen = (
                df_merged.groupby(["CLASIFICACION", "CATEGORIA"])[col_monto]
                .sum()
                .reset_index()
                .rename(columns={col_monto: empresa})
            )
            resultados.append(resumen)

        if not resultados:
            st.error("❌ No se pudo generar información consolidada.")
            return

        # --- Unir todas las empresas ---
        df_final = reduce(lambda l, r: pd.merge(l, r, on=["CLASIFICACION", "CATEGORIA"], how="outer"), resultados).fillna(0)
        df_final["TOTAL ACUMULADO"] = df_final[hojas_empresas].sum(axis=1)

        # --- Mostrar por clasificación ---
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

            for col in hojas_empresas + ["TOTAL ACUMULADO"]:
                df_clasif[col] = df_clasif[col].apply(lambda x: f"${x:,.2f}")

            with st.expander(f"🔹 {clasif}"):
                st.dataframe(df_clasif.drop(columns=["CLASIFICACION"]), use_container_width=True, hide_index=True)

        # --- Resumen final ---
        totales = {
            "ACTIVO": df_final[df_final["CLASIFICACION"] == "ACTIVO"]["TOTAL ACUMULADO"].sum(),
            "PASIVO": df_final[df_final["CLASIFICACION"] == "PASIVO"]["TOTAL ACUMULADO"].sum(),
            "CAPITAL": df_final[df_final["CLASIFICACION"] == "CAPITAL"]["TOTAL ACUMULADO"].sum(),
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
        st.markdown("### 📊 Resumen del Balance Consolidado")
        st.dataframe(resumen_final, use_container_width=True, hide_index=True)

        if abs(diferencia) < 1:
            st.success("✅ El balance está cuadrado (ACTIVO = PASIVO + CAPITAL).")
        else:
            st.error("❌ El balance no cuadra. Revisa los saldos individuales.")

    tabla_balance_por_empresa()



elif selected == "BALANCE GENERAL ACUMULADO":
   
    def tabla_balance_acumulado(total_social, total_inversiones, GOODWILL, balance_url, df_mapeo):
        iva_por_pagar = 0.0  # o el valor que definas en otra parte

        hojas_empresas = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]

        # --- Lectura del archivo Excel ---
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
                resumen = resumen.rename(columns={col_monto: hoja})
                data_empresas.append(resumen)

        if not data_empresas:
            st.warning("⚠️ No se encontraron datos en las hojas especificadas.")
            return

        # --- Consolidar todas las hojas ---
        from functools import reduce
        df_total = reduce(lambda left, right: pd.merge(left, right, on=["CLASIFICACION", "CATEGORIA"], how="outer"), data_empresas)
        df_total = df_total.fillna(0)
        df_total["ACUMULADO"] = df_total[[c for c in df_total.columns if c not in ["CLASIFICACION", "CATEGORIA"]]].sum(axis=1)
        df_total = df_total.rename(columns={"CATEGORIA": "CUENTA"})

        # --- Inicializar columnas ---
        df_total["DEBE"] = 0.0
        df_total["HABER"] = 0.0
        df_total["MANUAL"] = 0.0

        # --- Ajustes específicos por cuenta ---
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

        # Capital social (suma de total_social + total_inversiones)
        total_capital_social = total_social + total_inversiones
        df_total.loc[df_total["CUENTA"].str.contains("CAPITAL SOCIAL", case=False), "DEBE"] = total_capital_social

        # --- Crear estructura jerárquica ---
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

        # --- Reemplazar vacíos por 0 ---
        for col in ["DEBE", "HABER", "MANUAL"]:
            df_final[col] = pd.to_numeric(df_final[col], errors="coerce").fillna(0.0)

        # --- Calcular TOTALES ---
        df_final["TOTALES"] = (
            df_final["ACUMULADO"].replace("", 0).astype(float)
            + df_final["DEBE"].astype(float)
            - df_final["HABER"].astype(float)
            + df_final["MANUAL"].astype(float)
        )

        # --- Editor interactivo ---
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

        # --- Recalcular TOTALES tras edición ---
        for col in ["DEBE", "HABER", "MANUAL"]:
            df_editable[col] = pd.to_numeric(df_editable[col], errors="coerce").fillna(0.0)

        df_editable["TOTALES"] = (
            df_editable["ACUMULADO"].replace("", 0).astype(float)
            + df_editable["DEBE"].astype(float)
            - df_editable["HABER"].astype(float)
            + df_editable["MANUAL"].astype(float)
        )

        # --- Mostrar tabla final ---
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
        total_inversiones = "EHM-HOLDING"+UTAC
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
            df_total.to_excel(writer, index=False, sheet_name="Totales", startrow=0)
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














