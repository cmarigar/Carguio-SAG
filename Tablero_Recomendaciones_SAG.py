import streamlit as st
import pandas as pd

# Cargar datos (ajusta la ruta del archivo según sea necesario)
data_path = 'pi_inicial_op.csv'
data = pd.read_csv(data_path, index_col=0, parse_dates=True)
data = data.round(2)

# Filtrar los últimos 8 días
last_8_days_data = data.tail(8)

# Iniciar la aplicación Streamlit
st.title('Tablero Recomendaciones Carguío Bolas SAG')

with st.expander("Ver/Ocultar Tabla de Datos"):
    columnas_deseadas = [col for col in last_8_days_data.columns if col not in ['Tasa Desgaste SAG16', 'Tasa Desgaste SAG17']]
    # Crear un DataFrame temporal solo con las columnas deseadas
    datos_mostrados = last_8_days_data[columnas_deseadas]
    # Mostrar el DataFrame filtrado
    st.write(datos_mostrados)


#Se condiciona la condición de grind out
if (data['TPD SAG 16'].iloc[-1]==0) & (data['Reposicion SAG16'].iloc [-1]==0):
    data['Nivel bolas estimada SAG16'].iloc[-1] = data['Nivel bolas estimada SAG16'].iloc[-2]
    st.error('SAG16 en mantenimiento')
elif (data['TPD SAG 17'].iloc[-1]==0) & (data['Reposicion SAG17'].iloc [-1]==0):
    data['Nivel bolas estimada SAG17'].iloc[-1] = data['Nivel bolas estimada SAG17'].iloc[-2]
    st.error('SAG17 en mantenimiento')
else:
    st.write('Ambos SAG en funcionamiento')


# Se calcula nivel_bolas para el SAG16 con el valor de reposicion que lo haga estar dentro del rango 13% y 15% idealmente
consumo_acero_16 = data['Consumo acero SAG16'].iloc[-1]  # Último valor de la columna 'Consumo acero SAG16'
consumo_acero_17 = data['Consumo acero SAG17'].iloc[-1]  # Último valor de la columna 'Consumo acero SAG17'

def aproximacion(valor):
    return round(valor, 1)

# Título de la aplicación
st.markdown(' ')

#Tasas de desgaste SAG
st.markdown('#### Ingresar tasas de desgaste para los SAG')
st.write(f'Fecha: {data.index[-1].date()}')

# La interfaz se divide en dos columnas
col1_tasasag16, col2_tasasag17 = st.columns(2)
# En la primera columna, colocar la casilla de tasa de desgaste SAG16
tasa_sag16= col1_tasasag16.number_input('Tasa Desgaste SAG16', value=275.0, format="%.1f", step=0.1)
# En la segunda columna, colocar la casilla de tasa de desgaste SAG17
tasa_sag17 = col2_tasasag17.number_input('Tasa Desgaste SAG17', value=328.0, format="%.1f", step=0.1)
    
#Limites para el nivel de bolas SAG16
st.markdown('#### Ingresar límites para nivel de bolas SAG16')
st.write(f'Fecha: {data.index[-1].date()}')
# La interfaz se divide en dos columnas
col1_sag16, col2_sag16 = st.columns(2)
# En la primera columna, colocar la casilla de entrada para el límite inferior
lim_inf_16 = col1_sag16.number_input('Limite Inferior16 (%)', value=12.5, format="%.1f", step=0.1)
# En la segunda columna, colocar la casilla de entrada para el límite superior
lim_sup_16 = col2_sag16.number_input('Limite Superior16 (%)', value=15.0, format="%.1f", step=0.1)


#Limites para el nivel de bolas SAG17
st.markdown('#### Ingresar límites para nivel de bolas SAG17')
st.write(f'Fecha: {data.index[-1].date()}')

# La interfaz se divide en dos columnas
col1_sag17, col2_sag17 = st.columns(2)
# En la primera columna, colocar la casilla de entrada para el límite inferior
lim_inf_17 = col1_sag17.number_input('Limite Inferior17 (%)', value=12.5, format="%.1f", step=0.1)
# En la segunda columna, colocar la casilla de entrada para el límite superior
lim_sup_17 = col2_sag17.number_input('Limite Superior17 (%)', value=15.0, format="%.1f", step=0.1)

#Boton para validar las variables anteriores
if st.button('Validar'):
    if (tasa_sag16 >= 0) & (tasa_sag17 >= 0) & (lim_inf_16 >= 0) & (lim_sup_16 >= 0) & (lim_inf_17 >= 0) & (lim_sup_17 >= 0) :
        st.success(f'Tasas de desgaste válidas: {tasa_sag16} y {tasa_sag17}')
        data['Tasa Desgaste SAG16'].iloc[-1]=tasa_sag16
        data['Tasa Desgaste SAG17'].iloc[-1]=tasa_sag17
        #Como cambia la tasa de desgaste, tambien debe cambiar el consumo de acero
        data['Consumo acero SAG16'].iloc[-1]= (data["TPD SAG 16"].iloc[-1]* data['Tasa Desgaste SAG16'].iloc[-1])/1000
        consumo_acero_16 = data['Consumo acero SAG16'].iloc[-1]
        data['Consumo acero SAG17'].iloc[-1]=(data["TPD SAG 17"].iloc[-1]* data['Tasa Desgaste SAG17'].iloc[-1])/1000
        consumo_acero_17 = data['Consumo acero SAG17'].iloc[-1]
        #Si cambia el consumo de acero, cambia la variación de nivel de los SAG
        data["Variacion de nivel SAG16"].iloc[-1]=(data["Reposicion SAG16"].iloc[-1]-data["Consumo acero SAG16"].iloc[-1])/1000/19
        data["Variacion de nivel SAG17"].iloc[-1]=(data["Reposicion SAG17"].iloc[-1]-data["Consumo acero SAG17"].iloc[-1])/1000/19
        #Si cambia la variación de nivel, cambia el nivel de bolas del SAG
        fecha_actual=data.index[-1]
        fecha_anterior = fecha_actual - pd.Timedelta(days=1)
        data['Nivel bolas estimada SAG16'].iloc[-1]=data['Nivel bolas estimada SAG16'].iloc[-2] + data["Variacion de nivel SAG16"].iloc[-1]
        data['Nivel bolas estimada SAG17'].iloc[-1]=data['Nivel bolas estimada SAG17'].iloc[-2] + data["Variacion de nivel SAG17"].iloc[-1]
        st.success(f'Rango de nivel de bolas válido: {lim_inf_16}% y {lim_sup_16}%')
        st.success(f'Rango de nivel de bolas válido: {lim_inf_17}% y {lim_sup_17}%')
    else:
        st.error('Los números deben ser positivos')

st.markdown(' ')
lista_valores=[0, 12500, 25000]
valor_0, valor_12500, valor_25000=lista_valores

#Para el SAG16
st.markdown('#### Recomendaciones para SAG16')
st.write(f'Fecha: {data.index[-1].date()}')

for i in lista_valores:
    nivel_bolas_16 = data['Nivel bolas estimada SAG16'].iloc[-2] + (i - consumo_acero_16) / 1000 / 19
    nivel_bolas_16 = aproximacion(nivel_bolas_16)
    if lim_inf_16 < nivel_bolas_16 < lim_sup_16:
        if i==valor_0:
            st.success(f'Si la reposicion de acero es {valor_0}(Kg), el nivel de bolas es {nivel_bolas_16}%')
        elif i==valor_12500:
            st.success (f'Si la reposicion de acero es {valor_12500}(Kg), el nivel de bolas es {nivel_bolas_16}%')
        elif i==valor_25000:
            st.success (f'Si la reposicion de acero es {valor_25000}(Kg), el nivel de bolas es {nivel_bolas_16}%')
    else:
        # Si ninguna de las reposiciones hizo que nivel_bolas esté dentro del rango, se muestra un mensaje de error
        st.error(f'No se puede ajustar el valor de reposicion {i} (Kg) para que el nivel de bolas este dentro del rango {lim_inf_16}% y {lim_sup_16}%')

respuesta_16 = st.radio("¿Qué recomendación acepta para el SAG16?", ('0', '12,500','25,000','Ingresar recomendación'))

if respuesta_16 == 'Ingresar recomendación':
    respuesta_16_n = st.number_input("Ingrese la carga SAG16")
    if (respuesta_16_n >= 0):
        data.loc[data.index[-1], 'Reposicion SAG16'] = respuesta_16_n
        nivel_bolas_16 = data['Nivel bolas estimada SAG16'].iloc[-2] + (respuesta_16_n - consumo_acero_16) / 1000 / 19
        data.loc[data.index[-1], 'Nivel bolas estimada SAG16'] = nivel_bolas_16
        nivel_bolas_16 = aproximacion(nivel_bolas_16)
        st.success (f"Reposicion para SAG16 es {respuesta_16_n}(Kg) y el nivel de bolas es {nivel_bolas_16}%")
    else:
        st.error ('La reposición debe ser igual o mayor a cero (kg)')
else:
    respuesta_16 = respuesta_16.replace(',', '')
    respuesta_16=float(respuesta_16)
    if (respuesta_16==valor_0):
        data.loc[data.index[-1], 'Reposicion SAG16'] = valor_0
        nivel_bolas_16 = data['Nivel bolas estimada SAG16'].iloc[-2] + (valor_0 - consumo_acero_16) / 1000 / 19
        data.loc[data.index[-1], 'Nivel bolas estimada SAG16'] = nivel_bolas_16
        nivel_bolas_16 = aproximacion(nivel_bolas_16)
        st.write ((f"Reposicion para SAG16 es {respuesta_16}(Kg) y el nivel de bolas es {nivel_bolas_16}%, y se recomienda no cargar"))
    elif (respuesta_16 == valor_12500):
        data.loc[data.index[-1], 'Reposicion SAG16'] = valor_12500
        nivel_bolas_16 = data['Nivel bolas estimada SAG16'].iloc[-2] + (valor_12500 - consumo_acero_16) / 1000 / 19
        data.loc[data.index[-1], 'Nivel bolas estimada SAG16'] = nivel_bolas_16
        nivel_bolas_16 = aproximacion(nivel_bolas_16)
        st.write ((f"Reposicion para SAG16 es {respuesta_16}(Kg) y el nivel de bolas es {nivel_bolas_16}%, y se recomienda 1 carga T-A"))
    elif (respuesta_16==valor_25000):
        data.loc[data.index[-1], 'Reposicion SAG16'] = valor_25000
        nivel_bolas_16 = data['Nivel bolas estimada SAG16'].iloc[-2] + (valor_25000 - consumo_acero_16) / 1000 / 19
        data.loc[data.index[-1], 'Nivel bolas estimada SAG16'] = nivel_bolas_16
        nivel_bolas_16 = aproximacion(nivel_bolas_16)
        st.write ((f"Reposicion para SAG16 es {respuesta_16}(Kg) y el nivel de bolas es {nivel_bolas_16}%, y se recomienda 1 carga T-A + 1 carga TB"))


# Botón para validar reposicion
if st.button('Validar reposicion SAG16'):
    if (respuesta_16 >= 0) & (lim_inf_16 < nivel_bolas_16 < lim_sup_16):
        st.success(f'Reposicion SAG16 valida: {respuesta_16}(Kg)')
        data.loc[data.index[-1], 'Reposicion SAG16'] = respuesta_16
        data.loc[data.index[-1], 'Nivel bolas estimada SAG16'] = nivel_bolas_16
    else:
        st.error('La reposicion debe ser positivas')


#Variacion de nivel SAG = (Reposicion SAG - CONSUMO DE ACERO SAG)/1000/19
data.loc[data.index[-1],"Variacion de nivel SAG16"]=(data.loc[data.index[-1],"Reposicion SAG16"]-data.loc[data.index[-1],"Consumo acero SAG16"])/1000/19


#Para el SAG17
st.markdown('#### Recomendaciones SAG17')
st.write(f'Fecha: {data.index[-1].date()}')

for j in lista_valores:
    nivel_bolas_17 = data['Nivel bolas estimada SAG17'].iloc[-2] + (j - consumo_acero_17) / 1000 / 19
    nivel_bolas_17 = aproximacion(nivel_bolas_17)
    if lim_inf_17 < nivel_bolas_17 < lim_sup_17:
        if j==valor_0:
            st.success(f'Si la reposicion de acero es {valor_0}(Kg), el nivel de bolas es {nivel_bolas_17}%')
        elif j==valor_12500:
            st.success (f'Si la reposicion de acero es {valor_12500}(Kg), el nivel de bolas es {nivel_bolas_17}%')
        elif j==valor_25000:
            st.success (f'Si la reposicion de acero es {valor_25000}(Kg), el nivel de bolas es {nivel_bolas_17}%')
    else:
        # Si ninguna de las reposiciones hizo que nivel_bolas esté dentro del rango, se muestra un mensaje de error
        st.error(f'No se puede ajustar el valor reposicion {j}(Kg) para que el nivel de bolas esté dentro del rango {lim_inf_17}% y {lim_sup_17}%')


respuesta_17 = st.radio("¿Qué recomendación acepta para el SAG17?", ('0', '12,500','25,000','Ingresar recomendación'))

if respuesta_17 == 'Ingresar recomendación':
    respuesta_17_n = st.number_input("Ingrese la carga SAG17")
    data.loc[data.index[-1], 'Reposicion SAG17'] = respuesta_17_n
    nivel_bolas_17 = data['Nivel bolas estimada SAG17'].iloc[-2] + (respuesta_17_n - consumo_acero_17) / 1000 / 19
    data.loc[data.index[-1], 'Nivel bolas estimada SAG17'] = nivel_bolas_17
    nivel_bolas_17 = aproximacion(nivel_bolas_17)
    st.success (f"Reposicion para SAG17 es {respuesta_17_n}(Kg) y el nivel de bolas es {nivel_bolas_17}%")
else:
    respuesta_17 = respuesta_17.replace(',', '')
    respuesta_17=float(respuesta_17)
    if respuesta_17==valor_0:
        data.loc[data.index[-1], 'Reposicion SAG17'] = respuesta_17
        nivel_bolas_17 = data['Nivel bolas estimada SAG17'].iloc[-2] + (respuesta_17 - consumo_acero_17) / 1000 / 19
        data.loc[data.index[-1], 'Nivel bolas estimada SAG17'] = nivel_bolas_17
        nivel_bolas_17 = aproximacion(nivel_bolas_17)
        st.write ((f"Reposicion para SAG17 es {respuesta_17}(Kg) y el nivel de bolas es {nivel_bolas_17}%, se recomienda no cargar"))
    elif respuesta_17==valor_12500:
        data.loc[data.index[-1], 'Reposicion SAG17'] = respuesta_17
        nivel_bolas_17 = data['Nivel bolas estimada SAG17'].iloc[-2] + (respuesta_17 - consumo_acero_17) / 1000 / 19
        data.loc[data.index[-1], 'Nivel bolas estimada SAG17'] = nivel_bolas_17
        nivel_bolas_17 = aproximacion(nivel_bolas_17)
        st.write ((f"Reposicion para SAG17 es {respuesta_17}(Kg) y el nivel de bolas es {nivel_bolas_17}%, se recomienda 1 carga T-A"))
    elif respuesta_17==valor_25000:
        data.loc[data.index[-1], 'Reposicion SAG17'] = respuesta_17
        nivel_bolas_17 = data['Nivel bolas estimada SAG17'].iloc[-2] + (respuesta_17 - consumo_acero_17) / 1000 / 19
        data.loc[data.index[-1], 'Nivel bolas estimada SAG17'] = nivel_bolas_17
        nivel_bolas_17 = aproximacion(nivel_bolas_17)
        st.write ((f"Reposicion para SAG17 es {respuesta_17}(Kg) y el nivel de bolas es {nivel_bolas_17}%, se recomienda 1 carga T-A +1 carga TB"))

data.loc[data.index[-1],"Variacion de nivel SAG17"]=(data.loc[data.index[-1],"Reposicion SAG17"]-data.loc[data.index[-1],"Consumo acero SAG17"])/1000/19

# Botón para validar reposicion
if st.button('Validar reposicion SAG17'):
    if (respuesta_17 >= 0) & (lim_inf_17 < nivel_bolas_17 < lim_sup_17):
        st.success(f'Reposicion SAG17 valida: {respuesta_17}(Kg)')
        data.loc[data.index[-1], 'Reposicion SAG17'] = respuesta_17
        data.loc[data.index[-1], 'Nivel bolas estimada SAG17'] = nivel_bolas_17
    else:
        st.error('La reposicion debe ser positivas')



data.to_csv('pi_inicial_op.csv')
