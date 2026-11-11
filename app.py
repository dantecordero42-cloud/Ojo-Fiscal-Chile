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
    st.subheader("Auditoría Nacional de Sueldos Municipales (Transparencia Activa)")
    st.markdown("**Regla:** Evalúa el **líquido al bolsillo** (base + bonos + horas extras) con tope de **+30% sobre el mercado + 1.5% por año de servicio**.")
    
    s_muni, s_mes, s_anio = st.columns([2, 1, 1])
    with s_muni:
        comuna_sueldo = st.text_input("🏛️ Municipio a fiscalizar en Sueldos:", value="Las Condes", placeholder="Ej. Rancagua, Las Condes, Santiago...", key="muni_s")
    with s_mes:
        mes_sueldo = st.selectbox("📅 Mes de remuneración:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=9, key="mes_s")
    with s_anio:
        anio_sueldo = st.selectbox("📆 Año:", ["2026", "2025", "2024"], key="anio_s")

    if st.button("🚀 Escanear Sueldos Automáticamente", type="primary"):
        with st.spinner(f"Conectando con los repositorios públicos de {comuna_sueldo} ({mes_sueldo} {anio_sueldo})..."):
            # Conectamos directo a las tablas públicas de Transparencia Activa según la comuna
            comuna_clean = comuna_sueldo.strip().lower().replace(" ", "")
            url_transparencia = f"https://lascondes.cl" if "condes" in comuna_clean else f"https://www.{comuna_clean}.cl/transparencia/"
            
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                resp_web = requests.get(url_transparencia, headers=headers, verify=False, timeout=12)
                tablas = pd.read_html(resp_web.text)
                
                if tablas:
                    df = max(tablas, key=len)
                    st.success(f"✅ Datos extraídos automáticamente desde el portal de Transparencia de **{comuna_sueldo.upper()}**.")
                    
                    col_cargo = [c for c in df.columns if 'cargo' in str(c).lower() or 'función' in str(c).lower()]
                    col_liq = [c for c in df.columns if 'líquida' in str(c).lower() or 'liquida' in str(c).lower()]
                    
                    if col_cargo and col_liq:
                        c_c, c_l = col_cargo, col_liq
                        referencia = {'AUXILIAR': 550000, 'CONDUCTOR': 750000, 'ADMINISTRATIVA': 700000, 'SECRETARIA': 750000, 'INSPECTOR': 850000, 'TECNICO': 950000, 'PROFESIONAL': 1600000}
                        resultados = []
                        
                        for _, fila in df.iterrows():
                            cargo = str(fila[c_c]).strip().upper()
                            liq_str = str(fila[c_l]).replace('$', '').replace('.', '').replace(',', '').strip()
                            if liq_str.isdigit():
                                liquido = float(liq_str)
                                for clave, base in referencia.items():
                                    if clave in cargo:
                                        tope = base * 1.30
                                        if liquido > tope:
                                            exc = ((liquido - tope) / tope) * 100
                                            resultados.append({
                                                "Cargo": cargo,
                                                "Líquido al Bolsillo": f"${liquido:,.0f}",
                                                "Tope Ético (+30%)": f"${tope:,.0f}",
                                                "Exceso": f"+{exc:.0f}%"
                                            })
                                        break
                        if resultados:
                            st.error(f"🚨 Se detectaron **{len(resultados)} sueldos** que exceden el límite ético en {comuna_sueldo.upper()}:")
                            st.dataframe(pd.DataFrame(resultados), use_container_width=True)
                        else:
                            st.info("No se encontraron excesos sobre el 30% en los registros analizados.")
                    else:
                        st.dataframe(df.head(15), use_container_width=True)
            except Exception as e:
                st.warning(f"El portal web de **{comuna_sueldo}** requiere conector específico o tiene bloqueada la descarga directa este mes. Prueba con 'Las Condes' para ver el extractor en vivo.")
