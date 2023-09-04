
# Consultar en postgresql para obtener la información de los clientes
import psycopg2
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np  # Importar numpy


conn = psycopg2.connect(
    host="db.sskxgyimgyvtlkutppsi.supabase.co",
    database="postgres",
    user="postgres",
    password="nqhGKS75**1234"
)

cursor = conn.cursor()

# consulta de subs PRINCIPALES sin devices
cursor.execute("""

select description, age_range, count(*) 
from (
select c.*, g.description, EXTRACT(YEAR FROM AGE(current_date, birth_date)) AS "age",
case 
	when EXTRACT(YEAR FROM AGE(current_date, birth_date)) >= 0 and 
	EXTRACT(YEAR FROM AGE(current_date, birth_date))<= 18 then '[0-18]'
	when EXTRACT(YEAR FROM AGE(current_date, birth_date)) >= 19 and 
	EXTRACT(YEAR FROM AGE(current_date, birth_date)) <= 24 then '[19-24]'
	when EXTRACT(YEAR FROM AGE(current_date, birth_date)) >= 25 and 
	EXTRACT(YEAR FROM AGE(current_date, birth_date)) <= 50 then '[25-50]'
	when EXTRACT(YEAR FROM AGE(current_date, birth_date)) >= 51 and 
	EXTRACT(YEAR FROM AGE(current_date, birth_date)) <= 90 then '[51-90]'
	when EXTRACT(YEAR FROM AGE(current_date, birth_date)) > 90 then '>90'
end as age_range
from customers c 
left join genders g 
on g.id = c.gender_id 
where g.description in ('Masculino','Femenino')
and c.birth_date is not null
) as clasification
group by description, age_range
order by  age_range asc
""")

rows = cursor.fetchall()

consulta_1 = pd.DataFrame(rows)

column_names = [desc[0] for desc in cursor.description]
consulta_1.columns = column_names


cursor.execute("""
select r.city, sum(c.income_in_cents)/100 as total_income
from customers c 
inner join branches b 
on b.id = c.branch_id 
inner join regions r 
on r.id = b.region_id 
group by r.city
order by sum(c.income_in_cents)/100 desc
""")

rows = cursor.fetchall()

consulta_2= pd.DataFrame(rows)

column_names = [desc[0] for desc in cursor.description]
consulta_2.columns = column_names


cursor.execute("""
select g.description, count(c.id)
from customers c 
left join genders g 
on g.id = c.gender_id 
group by g.description
""")

rows = cursor.fetchall()

consulta_3= pd.DataFrame(rows)

column_names = [desc[0] for desc in cursor.description]
consulta_3.columns = column_names

cursor.execute("""
select b.branch_details, count(*) as customer_count
from customers c 
inner join branches b 
on b.id = c.branch_id 
group by b.branch_details
order by customer_count desc
limit 50
""")

rows = cursor.fetchall()

consulta_4= pd.DataFrame(rows)

column_names = [desc[0] for desc in cursor.description]
consulta_4.columns = column_names

st.sidebar.image('wompi_logo_withoutBK.png', use_column_width=True)


css = '''
<style>
    [data-testid="stSidebar"]{
        min-width: 400px;
        max-width: 800px;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)
# =======================================================================================
# ~ Gráfico 1
# =======================================================================================

# Crear un gráfico de barras agrupadas con Plotly Express para todos los datos
fig1 = px.bar(
    consulta_1, 
    x='age_range', 
    y='count', 
    color='description', 
    barmode='group',  # Utilizar barras agrupadas en lugar de apiladas
    labels={'age_range': 'Rango de Edad', 'count': 'Recuento', 'description': 'Filtro por género'},
    title='Distribución por Rango de Edad'
)

# Personalizar el gráfico
fig1.update_xaxes(type='category')  # Utilizar el eje X como categorías
fig1.update_traces(texttemplate='%{value}', textposition='outside')  # Colocar el recuento encima de las barras
# Guarda el eje Y sin prefijo K
fig1.update_layout(yaxis_tickformat='d')

# Quitar las líneas de cuadrícula en ambos ejes
fig1.update_xaxes(showgrid=False)
fig1.update_yaxes(showgrid=False)

fig1.update_layout(height=450,width= 500)  # Ajustar la altura



# =======================================================================================
# ~ Gráfico 2
# =======================================================================================

consulta_2['total_income'] = consulta_2['total_income'].apply(np.int64)

# Ordenar los datos por 'total_income' en orden descendente y tomar los 10 primeros registros (Top 10)
top_10 = consulta_2.sort_values(by='total_income', ascending=False).head(10)

# Crear un gráfico de barras horizontales con Plotly Express
fig2 = px.bar(
    top_10, 
    x='total_income', 
    y='city', 
    orientation='h',  # Barras horizontales
    labels={'total_income': 'Total de Ingresos', 'city': 'Ciudad'},
    title='Top 10 Ciudades con Mayor Total de Ingresos',
    category_orders={'city': top_10['city']}  # Ordenar las categorías por 'city'
)

# Personalizar el gráfico
fig2.update_xaxes(title_text='Total de Ingresos', showgrid=False)
fig2.update_yaxes(title_text='Ciudad', showgrid=False)

fig2.update_layout(height=450,width= 500)  # Ajustar la altura

# =======================================================================================
# ~ Gráfico 3, métricas
# =======================================================================================

st.button("Actualizar Datos")

col1, col2, col3,col4 = st.columns(4)
col1.metric("Clientes totales", "50.000","n% mes anterior")
col2.metric("Ingresos totales", "262.45B", "n% mes anterior")
col3.metric("Qty clientes Carabobo", "520", "-n% mes anterior")
col4.metric("Qty clientes Cundinamarca", "14004", "-n% mes anterior")


# =======================================================================================
# ~ Gráfico 4, pie chart
# =======================================================================================
# Crear un gráfico de pastel para la distribución por géneros
fig4 = px.pie(
    consulta_3,
    values='count',
    names='description',
    title='Distribución por Género de Clientes'
)

# Personalizar el gráfico
fig4.update_traces(textinfo='percent+label')


# =======================================================================================
# ~ Gráfico 5, barras
# =======================================================================================
# Crear un gráfico de pastel para la distribución por géneros
# Crear un gráfico de barras horizontales para consulta_4

fig5 = px.bar(
    consulta_4,
    x='branch_details',
    y='customer_count',
    labels={'count': 'Count', 'branch_details': 'Sucursales'},
    title='Distribución de clientes por sucursal'
)

# Personalizar el gráfico
fig5.update_xaxes(title_text='Count', showgrid=False)
fig5.update_yaxes(title_text='Sucursales', showgrid=False)
fig5.update_layout(height=600, width=800)

# Dividir la pantalla en dos columnas y mostrar los gráficos uno al lado del otro
col5, col6 = st.columns((5,2))

#col4, col5 = st.columns([5, 1])  # Columna 1: 5 partes, Columna 2: 1 parte, Columna 3: 1 parte


# Mostrar el gráfico de consulta_1 en la primera columna
col5.plotly_chart(fig1)

# Mostrar el gráfico de consulta_3 en la segunda columna
col6.plotly_chart(fig4)

st.plotly_chart(fig5)

