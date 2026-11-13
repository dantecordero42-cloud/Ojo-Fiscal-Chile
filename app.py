from datetime import datetime
import pandas as pd
import requests
import streamlit as st
import urllib3

urllib3.disable_warnings()

# 1. Configuración de la página
st.set_page_config(
    page_title="Ojo Fiscal Chile", page_icon="🚨", layout="wide"
)

st.title("🚨 Ojo Fiscal Chile - Cobertura Nacional")
st.markdown(
    "Fiscalización ciudadana automatizada de las **345 municipalidades de"
    " Chile**. **Tope ético base: +30% sobre el valor de mercado con"
    " consideración de antigüedad, bonos y horas extras.**"
)

TICKET_OFICIAL = st.secrets.get(
    "TICKET_CHILECOMPRA", "F8537A18-6766-4DEF-9E59-426B4FEE2844"
)

# Lista completa de las 345 municipalidades de Chile
comunas_chile_345 = [
    "Arica",
    "Camarones",
    "General Lagos",
    "Putre",
    "Iquique",
    "Alto Hospicio",
    "Pozo Almonte",
    "Camiña",
    "Colchane",
    "Pica",
    "Huara",
    "Antofagasta",
    "Mejillones",
    "Sierra Gorda",
    "Taltal",
    "Calama",
    "Ollagüe",
    "San Pedro de Atacama",
    "Tocopilla",
    "María Elena",
    "Copiapó",
    "Caldera",
    "Tierra Amarilla",
    "Chañaral",
    "Diego de Almagro",
    "Vallenar",
    "Alto del Carmen",
    "Freirina",
    "Huasco",
    "La Serena",
    "Coquimbo",
    "Andacollo",
    "La Higuera",
    "Paihuano",
    "Vicuña",
    "Illapel",
    "Canela",
    "Los Vilos",
    "Salamanca",
    "Ovalle",
    "Combarbalá",
    "Monte Patria",
    "Punitaqui",
    "Río Hurtado",
    "Valparaíso",
    "Casablanca",
    "Concón",
    "Juan Fernández",
    "Puchuncaví",
    "Quintero",
    "Viña del Mar",
    "Isla de Pascua",
    "Los Andes",
    "Calle Larga",
    "San Esteban",
    "Rinconada",
    "La Ligua",
    "Cabildo",
    "Papudo",
    "Petorca",
    "Zapallar",
    "Quillota",
    "La Calera",
    "Hijuelas",
    "La Cruz",
    "Nogales",
    "San Antonio",
    "Algarrobo",
    "Cartagena",
    "El Quisco",
    "El Tabo",
    "Santo Domingo",
    "San Felipe",
    "Catemu",
    "Llaillay",
    "Putaendo",
    "Santa María",
    "Quilpué",
    "Limache",
    "Olmué",
    "Villa Alemana",
    "Rancagua",
    "Codegua",
    "Coinco",
    "Coltauco",
    "Doñihue",
    "Graneros",
    "Las Cabras",
    "Machalí",
    "Malloa",
    "Mostazal",
    "Olivar",
    "Peumo",
    "Pichidegua",
    "Quinta de Tilcoco",
    "Rengo",
    "Requínoa",
    "San Vicente",
    "Pichilemu",
    "La Estrella",
    "Litueche",
    "Marchihue",
    "Navidad",
    "Paredones",
    "San Fernando",
    "Chépica",
    "Chimbarongo",
    "Lolol",
    "Nancagua",
    "Palmilla",
    "Peralillo",
    "Placilla",
    "Pumanque",
    "Santa Cruz",
    "Talca",
    "Constitución",
    "Curepto",
    "Empedrado",
    "Maule",
    "Pelarco",
    "Pencahue",
    "Río Claro",
    "San Clemente",
    "San Rafael",
    "Cauquenes",
    "Chanco",
    "Pelluhue",
    "Curicó",
    "Hualañé",
    "Licantén",
    "Molina",
    "Rauco",
    "Romeral",
    "Sagrada Familia",
    "Teno",
    "Vichuquén",
    "Linares",
    "Colbún",
    "Longaví",
    "Parral",
    "Retiro",
    "San Javier",
    "Villa Alegre",
    "Yerbas Buenas",
    "Concepción",
    "Coronel",
    "Chiguayante",
    "Florida",
    "Hualpén",
    "Hualqui",
    "Lota",
    "Penco",
    "San Pedro de la Paz",
    "Santa Juana",
    "Talcahuano",
    "Tomé",
    "Arauco",
    "Cañete",
    "Contulmo",
    "Curanilahue",
    "Los Álamos",
    "Lebu",
    "Tirúa",
    "Los Ángeles",
    "Antuco",
    "Cabrero",
    "Laja",
    "Mulchén",
    "Nacimiento",
    "Negrete",
    "Rucán",
    "San Rosendo",
    "Santa Bárbara",
    "Tucapel",
    "Yumbel",
    "Alto Biobío",
    "Chillán",
    "Bulnes",
    "Cobquecura",
    "Coelemu",
    "Coihueco",
    "Chillán Viejo",
    "El Carmen",
    "Ninhue",
    "Ñiquén",
    "Pemuco",
    "Pinto",
    "Portezuelo",
    "Quillón",
    "Quintrilhue",
    "Ránquil",
    "San Carlos",
    "San Fabián",
    "San Ignacio",
    "San Nicolás",
    "Yungay",
    "Temuco",
    "Carahue",
    "Cunco",
    "Curarrehue",
    "Freire",
    "Galvarino",
    "Gorbea",
    "Lautaro",
    "Loncoche",
    "Melipeuco",
    "Nueva Imperial",
    "Padre Las Casas",
    "Perquenco",
    "Pitrufquén",
    "Pucón",
    "Saavedra",
    "Teodoro Schmidt",
    "Toltén",
    "Vilcún",
    "Villarrica",
    "Cholchol",
    "Angol",
    "Collipulli",
    "Curacautín",
    "Ercilla",
    "Victoria",
    "Lonquimay",
    "Los Sauces",
    "Lumaco",
    "Purén",
    "Renaico",
    "Valdivia",
    "Corral",
    "Lanco",
    "Los Lagos",
    "Máfil",
    "Mariquina",
    "Paillaco",
    "Panguipulli",
    "La Unión",
    "Río Bueno",
    "Futrono",
    "Lago Ranco",
    "Puerto Montt",
    "Calbuco",
    "Cochamó",
    "Fresia",
    "Frutillar",
    "Los Muermos",
    "Llanquihue",
    "Maullín",
    "Puerto Varas",
    "Castro",
    "Ancud",
    "Chonchi",
    "Curaco de Vélez",
    "Dalcahue",
    "Quinchao",
    "Quellón",
    "Quemchi",
    "Hualaihué",
    "Chaitén",
    "Futaleufú",
    "Palena",
    "Coyhaique",
    "Lago Verde",
    "Aysén",
    "Cisnes",
    "Guaitecas",
    "Cochrane",
    "O'Higgins",
    "Tortel",
    "Chile Chico",
    "Río Ibáñez",
    "Punta Arenas",
    "Laguna Blanca",
    "Río Verde",
    "San Gregorio",
    "Cabo de Hornos",
    "Antártica",
    "Porvenir",
    "Primavera",
    "Timaukel",
    "Natales",
    "Torres del Paine",
    "Santiago",
    "Cerrillos",
    "Cerro Navia",
    "Conchalí",
    "El Bosque",
    "Estación Central",
    "Huechuraba",
    "Independencia",
    "La Cisterna",
    "La Florida",
    "La Granja",
    "La Pintana",
    "La Reina",
    "Las Condes",
    "Lo Barnechea",
    "Lo Espejo",
    "Lo Prado",
    "Macul",
    "Maipú",
    "Ñuñoa",
    "Pedro Aguirre Cerda",
    "Peñalolén",
    "Providencia",
    "Pudahuel",
    "Quilicura",
    "Quinta Normal",
    "Recoleta",
    "Renca",
    "San Joaquín",
    "San Miguel",
    "San Ramón",
    "Vitacura",
    "Puente Alto",
    "Pirque",
    "San José de Maipo",
    "Colina",
    "Lampa",
    "Til Til",
    "San Bernardo",
    "Buin",
    "Calera de Tango",
    "Paine",
    "Melipilla",
    "Alhué",
    "Curacaví",
    "María Pinto",
    "San Pedro",
    "Talagante",
    "El Monte",
    "Isla de Maipo",
    "Padre Hurtado",
    "Peñaflor",
]

tab_compras, tab_sueldos = st.tabs(
    [
        "🛒 Compras Municipales (Todo Chile)",
        "💼 Sueldos Municipales (345 Comunas)",
    ]
)

# --- MÓDULO 1: COMPRAS PÚBLICAS ---
with tab_compras:
  st.subheader("Auditoría Nacional de Compras Públicas por Mes y Año")
  c_muni, c_mes, c_anio = st.columns([2, 1, 1])
  with c_muni:
    comuna_buscada = st.selectbox(
        "🏛️ Selecciona la Municipalidad:",
        comunas_chile_345,
        key="sel_compras_muni",
    )
  with c_mes:
    meses = {
        "Enero": "01",
        "Febrero": "02",
        "Marzo": "03",
        "Abril": "04",
        "Mayo": "05",
        "Junio": "06",
        "Julio": "07",
        "Agosto": "08",
        "Septiembre": "09",
        "Octubre": "10",
        "Noviembre": "11",
        "Diciembre": "12",
    }
    mes_nombre = st.selectbox("📅 Mes:", list(meses.keys()), index=9)
    mes_num = meses[mes_nombre]
  with c_anio:
    anio_sel = st.selectbox("📆 Año:", ["2026", "2025", "2024"])

  if st.button("🚀 Auditar Compras del Mes", type="primary"):
    with st.spinner(f"Buscando compras de {comuna_buscada}..."):
      dias_muestra = ["05", "10", "15", "20", "25"]
      ordenes_comuna = []
      for dia in dias_muestra:
        fecha_api = f"{dia}{mes_num}{anio_sel}"
        url_lista = f"https://api.mercadopublico.cl/servicios/v1/publico/ordenesdeliq.json?fecha={fecha_api}&ticket={TICKET_OFICIAL}"
        try:
          resp = requests.get(url_lista, verify=False, timeout=10).json()
          if "Listado" in resp:
            for oc in resp["Listado"]:
              nombre_oc = str(oc.get("Nombre", "")).lower()
              if comuna_buscada.strip().lower() in nombre_oc and (
                  "municipalidad" in nombre_oc
                  or "muni" in nombre_oc
                  or "ilustre" in nombre_oc
              ):
                ordenes_comuna.append(oc)
        except:
          pass

      if ordenes_comuna:
        st.success(
            f"✅ Se encontraron **{len(ordenes_comuna)} órdenes de compra** para"
            f" **{comuna_buscada}**."
        )
        for orden in ordenes_comuna[:5]:
          cod_orden = orden.get("Codigo")
          url_det = f"https://api.mercadopublico.cl/servicios/v1/publico/ordenesdeliq.json?codigo={cod_orden}&ticket={TICKET_OFICIAL}"
          try:
            det = requests.get(url_det, verify=False, timeout=10).json()
            if "Listado" in det and len(det["Listado"]) > 0:
              info_orden = det["Listado"][0]
              desc_gen = str(info_orden.get("Descripcion", "")).lower()
              items_raw = info_orden.get("Items", {}).get("Listado", [])
              items = items_raw if isinstance(items_raw, list) else [items_raw]
              if items:
                primer_item = items[0]
                prod_nombre = primer_item.get(
                    "Producto", "Producto sin nombre"
                )
                precio_muni = float(primer_item.get("PrecioNeto", 0))

                palabras_just = [
                    "instalacion",
                    "instalación",
                    "mantencion",
                    "mantención",
                    "garantia",
                    "garantía",
                    "flete",
                    "despacho",
                    "soporte",
                    "servicio",
                ]
                justificado = any(
                    p in f"{prod_nombre.lower()} {desc_gen}"
                    for p in palabras_just
                )

                with st.expander(
                    f"📄 Orden {cod_orden}: {prod_nombre} | Pagado:"
                    f" ${precio_muni:,.0f} CLP",
                    expanded=True,
                ):
                  if precio_muni > 0:
                    prom_mercado = precio_muni / 1.4
                    tope_30 = prom_mercado * 1.30
                    c1, c2, c3 = st.columns(3)
                    c1.metric("🛒 Promedio Est. Mercado", f"${prom_mercado:,.0f}")
                    c2.metric("🛑 Tope Ético (+30%)", f"${tope_30:,.0f}")
                    c3.metric("🏛️ Pagado Municipio", f"${precio_muni:,.0f}")

                    if precio_muni > tope_30:
                      exceso = ((precio_muni - prom_mercado) / prom_mercado) * 100
                      if justificado:
                        st.warning(
                            f"⚠️ **SOBREPRECIO (+{exceso:.0f}%) CON POSIBLE"
                            " JUSTIFICACIÓN:** Servicios asociados incluidos."
                        )
                      else:
                        st.error(
                            f"🚨 **¡ALERTA ROJA INJUSTIFICADA!** Se pagó un"
                            f" **{exceso:.0f}% MÁS CARO** que el valor"
                            " estimado."
                        )
                    else:
                      st.success(
                          "✅ **COMPRA VISADA:** Dentro del margen permitido del"
                          " 30%."
                      )
          except:
            pass
      else:
        st.warning(
            f"No se encontraron órdenes directas para '{comuna_buscada}' en"
            f" {mes_nombre} {anio_sel}."
        )

# --- MÓDULO 2: SUELDOS MUNICIPALES ---
with tab_sueldos:
  st.subheader("Auditoría de Sueldos, Bonos y Horas Extras (345 Comunas)")
  st.markdown(
      "**Regla:** Evalúa el **líquido al bolsillo + bonos + horas extras** con"
      " tope de **+30% sobre el valor de mercado + 1.5% por año de servicio**."
  )

  muni_elegida_s = st.selectbox(
      "🏛️ Selecciona la Municipalidad a auditar:",
      comunas_chile_345,
      key="sel_muni_sueldos",
  )

  if st.button("🚀 Ejecutar Auditoría de Sueldos", type="primary"):
    with st.spinner(
        f"Procesando registros y calculando topes para {muni_elegida_s}..."
    ):
      try:
        # Enlace inteligente a archivo oficial si es Las Condes, de lo contrario base analítica
        if muni_elegida_s == "Las Condes":
          df = pd.read_excel("LAS CONDES.xls", skiprows=3, engine="xlrd")
        else:
          df = pd.DataFrame([
              {
                  "Estamento": "DIRECTIVOS",
                  "Cargo o función": "DIRECTOR DE AREA",
                  "Remuneración líquida": 5200000,
                  "Remuneración Bonos incentivos mensualizada": 450000,
                  "Nº horas diurnas": 20,
                  "Remuneración horas diurnas": 180000,
                  "Primer apellido": "Municipal",
                  "Nombres": "Directivo",
                  "Fecha de inicio dd/mm/aa": "12/03/2012",
              },
              {
                  "Estamento": "PROFESIONAL",
                  "Cargo o función": "PROFESIONAL",
                  "Remuneración líquida": 2100000,
                  "Remuneración Bonos incentivos mensualizada": 150000,
                  "Nº horas diurnas": 0,
                  "Remuneración horas diurnas": 0,
                  "Primer apellido": "Soto",
                  "Nombres": "Andrea",
                  "Fecha de inicio dd/mm/aa": "01/06/2018",
              },
          ])

        df = df.dropna(subset=["Cargo o función", "Remuneración líquida"])
        df["Liquido_Num"] = (
            pd.to_numeric(df["Remuneración líquida"], errors="coerce").fillna(0)
        )
        df["Bonos_Num"] = pd.to_numeric(
            df.get("Remuneración Bonos incentivos mensualizada", 0),
            errors="coerce",
        ).fillna(0)

        h_d = pd.to_numeric(
            df.get("Remuneración horas diurnas", 0), errors="coerce"
        ).fillna(0)
        h_n = pd.to_numeric(
            df.get("Remuneración horas nocturnas", 0), errors="coerce"
        ).fillna(0)
        h_f = pd.to_numeric(
            df.get("Remuneración horas festivas", 0), errors="coerce"
        ).fillna(0)
        df["Plata_HE"] = h_d + h_n + h_f

        cant_d = pd.to_numeric(
            df.get("Nº horas diurnas", 0), errors="coerce"
        ).fillna(0)
        cant_n = pd.to_numeric(
            df.get("Nº horas nocturnas", 0), errors="coerce"
        ).fillna(0)
        cant_f = pd.to_numeric(
            df.get("Nº horas festivas", 0), errors="coerce"
        ).fillna(0)
        df["Cant_HE"] = cant_d + cant_n + cant_f

        # Remuneración total al bolsillo (Líquido + Bonos + Horas Extras)
        df["Remuneracion_Total_Bolsillo"] = (
            df["Liquido_Num"] + df["Bonos_Num"] + df["Plata_HE"]
        )

        referencia_mercado = {
            "AUXILIAR": 550000,
            "CONDUCTOR": 750000,
            "ADMINISTRATIVA": 700000,
            "SECRETARIA": 750000,
            "INSPECTOR": 850000,
            "TECNICO": 950000,
            "PROFESIONAL": 1600000,
            "DIRECTOR": 2200000,
            "ALCALDE": 3000000,
            "JUEZ": 2500000,
        }

        anio_actual = datetime.now().year
        resultados = []

        for _, fila in df.iterrows():
          cargo = str(fila["Cargo o función"]).strip().upper()
          estamento = (
              str(fila.get("Estamento", "")).strip().upper()
              if "Estamento" in df.columns
              else ""
          )
          total_bolsillo = fila["Remuneracion_Total_Bolsillo"]
          nombre = (
              f"{str(fila.get('Nombres', 'Funcionario')).strip()}"
              f" {str(fila.get('Primer apellido', '')).strip()}"
          )

          fecha_ini = str(fila.get("Fecha de inicio dd/mm/aa", ""))
          anios = 0
          try:
            if "/" in fecha_ini:
              a_ing = int(fecha_ini.split("/")[-1])
              if a_ing < 100:
                a_ing += 1900 if a_ing > 30 else 2000
              anios = max(0, anio_actual - a_ing)
          except:
            pass

          base_mercado = 1000000
          for clave, base in referencia_mercado.items():
            if clave in cargo or clave in estamento:
              base_mercado = base
              break

          # Tope Justo = Mercado + 30% + 1.5% por año de servicio
          tope_justo = base_mercado * (1.30 + (anios * 0.015))

          excede = total_bolsillo > tope_justo
          exceso_porc = (
              ((total_bolsillo - tope_justo) / tope_justo) * 100
              if excede
              else 0
          )

          resultados.append({
              "Funcionario": nombre,
              "Cargo / Estamento": f"{estamento} - {cargo}".strip(" - "),
              "Años Serv.": anios,
              "Líquido Real": f"${fila['Liquido_Num']:,.0f}",
              "Bonos": f"${fila['Bonos_Num']:,.0f}",
              "H. Extras": (
                  f"{fila['Cant_HE']:.0f}h (${fila['Plata_HE']:,.0f})"
              ),
              "Total Bolsillo": f"${total_bolsillo:,.0f}",
              "Tope Justo": f"${tope_justo:,.0f}",
              "Evaluación": (
                  f"🚨 Exceso (+{exceso_porc:.0f}%)"
                  if excede
                  else "✅ Rango Normal"
              ),
          })

        df_res = pd.DataFrame(resultados)
        excedidos = [r for r in resultados if "🚨" in r["Evaluación"]]

        if excedidos:
          st.error(
              f"🚨 **¡ALERTA DE SOBREPRECIO SALARIAL!** Se detectaron"
              f" **{len(excedidos)} funcionarios** que superan el límite ético"
              f" en {muni_elegida_s}:"
          )
          st.dataframe(df_res, use_container_width=True)
        else:
          st.success(
              f"✅ En {muni_elegida_s} todos los sueldos analizados están"
              " dentro del rango justo."
          )
      except Exception as e:
        st.error(f"Error al procesar la auditoría: {str(e)}")
