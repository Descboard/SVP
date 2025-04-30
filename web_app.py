from flask import Flask, jsonify, render_template, request, send_file
import csv
import os
import io
from datetime import datetime

app = Flask(__name__)

# Ruta principal
@app.route('/')
def home():
    return render_template('index.html')  # Esto carga la vista HTML 
    {
        "status": "ok",
        "message": "API de reconocimiento de placas. Consulta /api/placas o /placas"
    }

# Ruta API en JSON
@app.route('/api/placas')
def obtener_placas():
    archivo = 'registros.csv'
    datos = []

    if os.path.exists(archivo):
        with open(archivo, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for fila in reader:
                try:
                    certeza = float(fila['Certeza'])
                    if certeza >= 50:
                        datos.append(fila)
                except ValueError:
                    continue
    return jsonify(datos)

# Vista web con filtros y paginación
@app.route('/placas')
def mostrar_placas():
    archivo = 'registros.csv'
    registros = []

    filtro_placa = request.args.get('placa', '').strip().upper()
    filtro_fecha = request.args.get('fecha', '').strip()

    if os.path.exists(archivo):
        with open(archivo, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for fila in reader:
                try:
                    certeza = float(fila['Certeza'])
                    if certeza >= 50:
                        if (not filtro_placa or filtro_placa in fila['Placa'].upper()) and \
                           (not filtro_fecha or fila['Fecha'] == filtro_fecha):
                            registros.append(fila)
                except ValueError:
                    continue

    # Paginación
    page = int(request.args.get('page', 1))
    per_page = 10
    total = len(registros)
    registros_pagina = registros[(page - 1) * per_page : page * per_page]

    return render_template('tabla.html', registros=registros_pagina, page=page, total=total,
                           per_page=per_page, filtro_placa=filtro_placa, filtro_fecha=filtro_fecha)

# Nueva ruta para exportar CSV con los filtros aplicados
@app.route('/exportar')
def exportar_csv():
    archivo = 'registros.csv'
    registros = []

    filtro_placa = request.args.get('placa', '').strip().upper()
    filtro_fecha = request.args.get('fecha', '').strip()

    if os.path.exists(archivo):
        with open(archivo, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for fila in reader:
                try:
                    certeza = float(fila['Certeza'])
                    if certeza >= 50:
                        if (not filtro_placa or filtro_placa in fila['Placa'].upper()) and \
                           (not filtro_fecha or fila['Fecha'] == filtro_fecha):
                            registros.append(fila)
                except ValueError:
                    continue

    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['Fecha', 'Hora', 'Placa', 'Certeza'])
    writer.writeheader()
    writer.writerows(registros)
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='placas_filtradas.csv'
    )

# Ejecutar app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
