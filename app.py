import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import urllib3
urllib3.disable_warnings()

st.set_page_config(page_title="Ojo Fiscal Chile", page_icon="🚨", layout="wide")

st.title("🚨 Ojo Fiscal Chile")
st.markdown("Control ciudadano automatizado de gastos públicos. **Tope ético base: +30% sobre el valor de mercado privado.**")

TICKET_OFICIAL = st.secrets.get("TICKET_CHILECOMPRA", "F8537A18-6766-4DEF-9E59-426B4FEE2844")

tab_compras, tab_sueldos = st.tabs(["🛒 Compras Públicas (En Vivo)", "💼 Sueldos Municipales (Planta y Contrata)"])

with tab_compras:
    st.subheader("Auditoría Automática en Mercado Público")
    col_muni, col_fecha = st.columns(2)
    with col_muni:
        municipios = {
            "Ilustre Municipalidad de Rancagua": "7334",
            "Ilustre Municipalidad de Las Condes": "7296",
            "Ilustre Municipalidad de Santiago": "7352",
            "Ilustre Municipalidad de Maipú": "7304"
        }
        muni_elegida = st.selectbox("🏛️ Selecciona el Municipio a auditar:", list(municipios.keys()))
        codigo_organismo = municipios[muni_elegida]
        
    with col_fecha:
        fecha_consulta = st.date_input("📅 Fecha de las órdenes de compra:", datetime.today())
        fecha_str = fecha_consulta.strftime("%d%m%Y")

    if st.button("🚀 Escanear Compras del Municipio Ahora", type="primary"):
        with st.spinner(f"Conectando con ChileCompra para auditar {muni_elegida}..."):
            url_lista = f"https://mercadopublico.cl{fecha_str}&CodigoOrganismo={codigo_organismo}&ticket={TICKET_OFICIAL}"
            try:
                resp = requests.get(url_lista, verify=False, timeout=15).json()
                if 'Listado' in resp and len(resp['Listado']) > 0:
                    ordenes = resp['Listado']
                    st.info(f"Se encontraron **{len(ordenes)} órdenes de compra** ese día. Analizando las primeras 5...")
                    for orden in ordenes[:5]:
                        cod_orden = orden['Codigo']
                        url_det = f"https://mercadopublico.cl{cod_orden}&ticket={TICKET_OFICIAL}"
                        det = requests.get(url_det, verify=False, timeout=15).json()
                        if 'Listado' in det and len(det['Listado']) > 0:
                            info_orden = det['Listado'][0] if isinstance(det['Listado'], list) else det['Listado']
                            descripcion_general = str(info_orden.get('Descripcion', '')).lower()
                            items_raw = info_orden.get('Items', {}).get('Listado', [])
                            items = items_raw if isinstance(items_raw, list) else [items_raw]
                            if items and len(items) > 0:
                                primer_item = items[0]
                                prod_nombre = primer_item.get('Producto', 'Producto sin nombre')
                                precio_muni = float(primer_item.get('PrecioNeto', 0))
                                palabras_just = ['instalacion', 'instalación', 'mantencion', 'mantención', 'garantia', 'garantía', 'flete', 'despacho', 'soporte', 'servicio']
                                justificado = any(p in f"{prod_nombre.lower()} {descripcion_general}" for p in palabras_just)
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
                                                st.warning(f"⚠️ **SOBREPRECIO (+{exceso:.0f}%) CON POSIBLE JUSTIFICACIÓN:** Incluye servicios adicionales. Requiere revisión.")
                                            else:
                                                st.error(f"🚨 **¡ALERTA ROJA INJUSTIFICADA!** Se pagó un **{exceso:.0f}% MÁS CARO** que el retail.")
                                                texto_denuncia = f"🚨 ALERTA OJO FISCAL CHILE\n🏛️ Institución: {muni_elegida}\n📦 Compra: {prod_nombre} (Orden {cod_orden})\n🛒 Valor real en Chile: ${prom_mercado:,.0f}\n💸 Pagado por el Estado: ${precio_muni:,.0f} (+{exceso:.0f}% de sobreprecio)\n#OjoFiscalChile #TransparenciaChile"
                                                st.code(texto_denuncia, language="text")
                                        else:
                                            st.success("✅ **COMPRA VISADA:** Dentro del margen permitido del 30%.")
                                    else:
                                        st.write("ℹ️ Producto especializado o servicio técnico sin equivalente directo en retail.")
                else:
                    st.warning("No hay órdenes emitidas en esta fecha exacta. Prueba seleccionando un día hábil anterior.")
            except Exception as e:
                st.error("Error de conexión con Mercado Público. Intenta nuevamente en unos segundos.")

with tab_sueldos:
    st.subheader("Auditoría de Sueldos Líquidos vs. Mercado Privado")
    st.markdown("""
    **Regla de Cálculo Justo:** 
    * Evalúa el **sueldo líquido real al bolsillo** (base + bonos + horas extras).
    * Aplica **+30% de margen máximo** sobre el mercado privado + **+1.5% adicional por cada año de servicio**.
    """)
    archivo_csv = st.file_uploader("📂 Sube la planilla CSV de Transparencia Activa de cualquier municipio", type=["csv"])
    if archivo_csv is not None:
        try:
            df = pd.read_csv(archivo_csv, skiprows=3)
            df = df.dropna(subset=['Cargo o función', 'Remuneración líquida'])
            df['Liquido_Num'] = pd.to_numeric(df['Remuneración líquida'], errors='coerce').fillna(0)
            df['Bonos_Num'] = pd.to_numeric(df.get('Remuneración Bonos incentivos mensualizada', 0), errors='coerce').fillna(0)
            h_diurnas = pd.to_numeric(df.get('Remuneración horas diurnas', 0), errors='coerce').fillna(0)
            h_nocturnas = pd.to_numeric(df.get('Remuneración horas nocturnas', 0), errors='coerce').fillna(0)
            h_festivas = pd.to_numeric(df.get('Remuneración horas festivas', 0), errors='coerce').fillna(0)
            df['Plata_HE'] = h_diurnas + h_nocturnas + h_festivas
            cant_d = pd.to_numeric(df.get('Nº horas diurnas', 0), errors='coerce').fillna(0)
            cant_n = pd.to_numeric(df.get('Nº horas nocturnas', 0), errors='coerce').fillna(0)
            cant_f = pd.to_numeric(df.get('Nº horas festivas', 0), errors='coerce').fillna(0)
            df['Cant_HE'] = cant_d + cant_n + cant_f
            referencia_mercado = {
                'AUXILIAR': 550000,
                'CONDUCTOR': 750000,
                'ADMINISTRATIVA': 700000,
                'SECRETARIA': 750000,
                'INSPECTOR': 850000,
                'TECNICO': 950000,
                'PROFESIONAL': 1600000
            }
            anio_actual = datetime.now().year
            resultados_alerta = []
            for _, fila in df.iterrows():
                cargo = str(fila['Cargo o función']).strip().upper()
                liquido = fila['Liquido_Num']
                bonos = fila['Bonos_Num']
                plata_he = fila['Plata_HE']
                cant_he = fila['Cant_HE']
                nombre = f"{str(fila['Nombres']).strip()} {str(fila['Primer apellido']).strip()}"
                fecha_ini_str = str(fila.get('Fecha de inicio dd/mm/aa', ''))
                anios_servicio = 0
                try:
                    if '/' in fecha_ini_str:
                        anio_ingreso = int(fecha_ini_str.split('/')[-1])
                        if anio_ingreso < 100:
                            anio_ingreso += 1900 if anio_ingreso > 30 else 2000
                        anios_servicio = max(0, anio_actual - anio_ingreso)
                except:
                    anios_servicio = 0
                for clave, base_privada in referencia_mercado.items():
                    if clave in cargo:
                        factor_antiguedad = anios_servicio * 0.015
                        tope_justo = base_privada * (1.30 + factor_antiguedad)
                        if liquido > tope_justo:
                            exceso_pct = ((liquido - tope_justo) / tope_justo) * 100
                            resultados_alerta.append({
                                "Funcionario": nombre,
                                "Cargo": cargo,
                                "Años Servicio": anios_servicio,
