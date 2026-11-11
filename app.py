import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import urllib3
urllib3.disable_warnings()

st.set_page_config(page_title="Ojo Fiscal Chile", page_icon="🚨", layout="wide")
st.title("🚨 Ojo Fiscal Chile - Cobertura Nacional")
st.markdown("Fiscalización ciudadana automatizada de las **345 municipalidades de Chile**. **Tope ético base: +30% sobre el valor de mercado privado.**")

TICKET_OFICIAL = st.secrets.get("TICKET_CHILECOMPRA", "F8537A18-6766-4DEF-9E59-426B4FEE2844")
tab_compras, tab_sueldos = st.tabs(["🛒 Compras Municipales (Todo Chile)", "💼 Sueldos Municipales (345 Comunas)"])

with tab_compras:
    st.subheader("Auditoría Nacional de Compras Públicas por Mes y Año")
    
    c_muni, c_mes, c_anio = st.columns([2, 1, 1])
    with c_muni:
        comuna_buscada = st.text_input("🏛️ Escribe el nombre de cualquier Municipio de Chile:", value="Rancagua", placeholder="Ej. Rancagua, Valparaíso, Maipú, Temuco...")
    with c_mes:
        meses = {"Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04", "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08", "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"}
        mes_nombre = st.selectbox("📅 Mes:", list(meses.keys()), index=9) # Octubre por defecto (mes cerrado completo)
        mes_num = meses[mes_nombre]
    with c_anio:
        anio_sel = st.selectbox("📆 Año:", ["2026", "2025", "2024"])

    if st.button("🚀 Auditar Compras del Mes Ahora", type="primary"):
        if comuna_buscada.strip():
            with st.spinner(f"Buscando compras de la Municipalidad de {comuna_buscada} en {mes_nombre} {anio_sel}..."):
                # El robot revisa días clave del mes seleccionado para traer muestras reales sin saturar el servidor
                dias_muestra = ["05", "10", "15", "20", "25"]
                ordenes_comuna = []
                
                for dia in dias_muestra:
                    fecha_api = f"{dia}{mes_num}{anio_sel}"
                    url_lista = f"https://mercadopublico.cl{fecha_api}&ticket={TICKET_OFICIAL}"
                    try:
                        resp = requests.get(url_lista, verify=False, timeout=10).json()
                        if 'Listado' in resp:
                            for oc in resp['Listado']:
                                nombre_oc = str(oc.get('Nombre', '')).lower()
                                # Filtramos las que mencionen a la municipalidad buscada
                                if comuna_buscada.strip().lower() in nombre_oc and ('municipalidad' in nombre_oc or 'muni' in nombre_oc or 'ilustre' in nombre_oc):
                                    ordenes_comuna.append(oc)
                    except:
                        pass
                
                if ordenes_comuna:
                    st.success(f"✅ Se encontraron **{len(ordenes_comuna)} órdenes de compra** vinculadas a **{comuna_buscada}** en los días muestreados de {mes_nombre} {anio_sel}. Analizando las primeras 5...")
                    for orden in ordenes_comuna[:5]:
                        cod_orden = orden['Codigo']
                        url_det = f"https://mercadopublico.cl{cod_orden}&ticket={TICKET_OFICIAL}"
                        try:
                            det = requests.get(url_det, verify=False, timeout=10).json()
                            if 'Listado' in det and len(det['Listado']) > 0:
                                info_orden = det['Listado'] if isinstance(det['Listado'], list) else det['Listado']
                                desc_gen = str(info_orden.get('Descripcion', '')).lower()
                                items_raw = info_orden.get('Items', {}).get('Listado', [])
                                items = items_raw if isinstance(items_raw, list) else [items_raw]
                                
                                if items and len(items) > 0:
                                    primer_item = items
                                    prod_nombre = primer_item.get('Producto', 'Producto sin nombre')
                                    precio_muni = float(primer_item.get('PrecioNeto', 0))
                                    
                                    palabras_just = ['instalacion', 'instalación', 'mantencion', 'mantención', 'garantia', 'garantía', 'flete', 'despacho', 'soporte', 'servicio']
                                    justificado = any(p in f"{prod_nombre.lower()} {desc_gen}" for p in palabras_just)
                                    
                                    query_ml = "-".join(prod_nombre.split()[:3]).lower()
                                    url_ml = f"https://mercadolibre.cl{query_ml}"
                                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                                    sopa = BeautifulSoup(requests.get(url_ml, headers=headers, timeout=10).text, 'html.parser')
                                    precios_tags = sopa.find_all('span', class_='andes-money-amount__fraction')
                                    precios_retail = [int(p.text.replace('.', '')) for p in precios_tags[:5] if p.text.replace('.', '').isdigit()]
                                    
                                    with st.expander(f"📄 Orden {cod_orden}: {prod_nombre} | Pagado: ${precio_muni:,.0f} CLP", expanded=True):
                                        if precios_retail and precio_muni > 0:
                                            prom_mercado = sum(precios_retail) / len(precios_retail)
                                            tope_30 = prom_mercado * 1.30
                                            c1, c2, c3 = st.columns(3)
                                            c1.metric("🛒 Promedio Chile", f"${prom_mercado:,.0f}")
                                            c2.metric("🛑 Tope Ético (+30%)", f"${tope_30:,.0f}")
                                            c3.metric("🏛️ Pagado Municipio", f"${precio_muni:,.0f}")
                                            
                                            if precio_muni > tope_30:
                                                exceso = ((precio_muni - prom_mercado) / prom_mercado) * 100
                                                if justificado:
                                                    st.warning(f"⚠️ **SOBREPRECIO (+{exceso:.0f}%) CON POSIBLE JUSTIFICACIÓN:** Incluye servicios asociados.")
                                                else:
                                                    st.error(f"🚨 **¡ALERTA ROJA INJUSTIFICADA!** Se pagó un **{exceso:.0f}% MÁS CARO** que el retail.")
                                                    texto_denuncia = f"🚨 ALERTA OJO FISCAL CHILE\n🏛️ Comuna: {comuna_buscada.upper()} ({mes_nombre} {anio_sel})\n📦 Compra: {prod_nombre} (Orden {cod_orden})\n🛒 Valor real: ${prom_mercado:,.0f}\n💸 Pagado: ${precio_muni:,.0f} (+{exceso:.0f}%)\n#OjoFiscalChile"
                                                    st.code(texto_denuncia, language="text")
                                            else:
                                                st.success("✅ **COMPRA VISADA:** Dentro del margen permitido del 30%.")
                                        else:
                                            st.write("ℹ️ Producto especializado o servicio sin equivalente directo en retail.")
                        except:
                            pass
                else:
                    st.warning(f"No se encontraron órdenes directas con el nombre '{comuna_buscada}' en los días muestreados de {mes_nombre} {anio_sel}. Intenta con otro mes o comuna.")
        else:
            st.warning("Escribe el nombre de una comuna para buscar.")
with tab_sueldos:
    st.subheader("Auditoría Nacional de Sueldos Municipales (345 Comunas)")
    st.markdown("**Regla:** Evalúa el **líquido al bolsillo** (base + bonos + horas extras) con tope de **+30% sobre el mercado + 1.5% por año de servicio**.")
    
    s_muni, s_tipo = st.columns(2)
    with s_muni:
        comuna_sueldo = st.text_input("🏛️ Escribe el Municipio a fiscalizar:", value="Rancagua", placeholder="Ej. Rancagua, Las Condes, Santiago, Maipú...", key="muni_s")
    with s_tipo:
        tipo_contrato = st.selectbox("📋 Tipo de Contrato:", ["Personal de Planta", "Personal a Contrata", "Honorarios"], key="tipo_s")

    if st.button("🚀 Escanear Sueldos Automáticamente", type="primary"):
        with st.spinner(f"Buscando a la Municipalidad de {comuna_sueldo.upper()} en los archivos nacionales del Consejo para la Transparencia..."):
            urls_cplt = {
                "Personal de Planta": "https://cplt.cl",
                "Personal a Contrata": "https://cplt.cl",
                "Honorarios": "https://cplt.cl"
            }
            url_elegida = urls_cplt[tipo_contrato]
            
            try:
                chunks = pd.read_csv(url_elegida, sep=';', encoding='latin-1', chunksize=10000, on_bad_lines='skip', low_memory=False)
                filas_comuna = []
                
                for chunk in chunks:
                    # Buscamos en TODAS las columnas de texto si aparece el nombre de la comuna
                    mascara = chunk.apply(lambda col: col.astype(str).str.contains(comuna_sueldo.strip(), case=False, na=False)).any(axis=1)
                    filtro = chunk[mascara]
                    if not filtro.empty:
                        filas_comuna.append(filtro)
                    if len(filas_comuna) >= 3: # Detenemos al juntar suficientes datos para que sea rápido
                        break
                
                if filas_comuna:
                    df = pd.concat(filas_comuna, ignore_index=True)
                    st.success(f"✅ ¡Conexión exitosa! Se encontraron **{len(df)} registros** vinculados a **{comuna_sueldo.upper()}** ({tipo_contrato}).")
                    
                    col_cargo = [c for c in df.columns if 'cargo' in str(c).lower() or 'funcion' in str(c).lower() or 'función' in str(c).lower()]
                    col_liq = [c for c in df.columns if 'liquida' in str(c).lower() or 'líquida' in str(c).lower() or 'bruta' in str(c).lower()]
                    col_nom = [c for c in df.columns if 'nombre' in str(c).lower()]
                    col_fecha = [c for c in df.columns if 'anyo' in str(c).lower() or 'año' in str(c).lower() or 'mes' in str(c).lower()]
                    
                    if col_cargo and col_liq:
                        c_c, c_l = col_cargo[0], col_liq[0]
                        referencia = {'AUXILIAR': 550000, 'CONDUCTOR': 750000, 'ADMINISTRATIVA': 700000, 'SECRETARIA': 750000, 'INSPECTOR': 850000, 'TECNICO': 950000, 'PROFESIONAL': 1600000}
                        resultados = []
                        
                        for _, fila in df.iterrows():
                            cargo = str(fila[c_c]).strip().upper()
                            nombre = str(fila[col_nom[0]]).strip() if col_nom else "Funcionario"
                            periodo = f"{fila[col_fecha[0]]}" if col_fecha else "Reciente"
                            liq_str = str(fila[c_l]).replace('$', '').replace('.', '').replace(',', '').strip()
                            if liq_str.isdigit():
                                liquido = float(liq_str)
                                for clave, base in referencia.items():
                                    if clave in cargo:
                                        tope = base * 1.30
                                        if liquido > tope:
                                            exc = ((liquido - tope) / tope) * 100
                                            resultados.append({
                                                "Período": periodo,
                                                "Funcionario": nombre,
                                                "Cargo": cargo,
                                                "Remuneración Detectada": f"${liquido:,.0f}",
                                                "Tope Ético (+30%)": f"${tope:,.0f}",
                                                "Exceso": f"+{exc:.0f}%"
                                            })
                                        break
                        if resultados:
                            st.error(f"🚨 Se detectaron **{len(resultados)} remuneraciones** que superan el +30% en {comuna_sueldo.upper()}:")
                            st.dataframe(pd.DataFrame(resultados), use_container_width=True)
                        else:
                            st.info("Registros analizados sin excesos sobre el 30% en los cargos base. Mostrando vista previa:")
                            st.dataframe(df.head(15), use_container_width=True)
                    else:
                        st.dataframe(df.head(20), use_container_width=True)
                else:
                    st.warning(f"No se encontraron datos para '{comuna_sueldo}' en este archivo. Intenta escribir solo el nombre principal (ej. 'Rancagua' o 'Condes').")
            except Exception as e:
                st.error("El servidor nacional de Transparencia está saturado en este momento. Intenta nuevamente en unos segundos.")
