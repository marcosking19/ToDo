from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Base de datos en memoria
tareas = []
contador_id = 1

# Plantilla HTML incrustada
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestor de Tareas (ToDo)</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1, h2 { color: #0056b3; }
        form { margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: #e9f7ef; }
        form div { margin-bottom: 10px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="number"], textarea, select {
            width: calc(100% - 22px);
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #28a745;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #218838;
        }
        .task-list { margin-top: 20px; }
        .task-item {
            background-color: #f9f9f9;
            border: 1px solid #eee;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .task-item.completed { background-color: #d4edda; border-color: #c3e6cb; }
        .task-item.in-progress { background-color: #fff3cd; border-color: #ffeeba; }
        .task-item .details { flex-grow: 1; }
        .task-item .actions button { margin-left: 5px; background-color: #007bff; }
        .task-item .actions button.delete { background-color: #dc3545; }
        .task-item .actions button:hover { opacity: 0.9; }
        .status-select { padding: 5px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Gestor de Tareas 📝</h1>

        <h2>Nueva Tarea</h2>
        <form id="task-form">
            <div>
                <label for="titulo">Título:</label>
                <input type="text" id="titulo" name="titulo" required>
            </div>
            <div>
                <label for="numero">Número (entero positivo):</label>
                <input type="number" id="numero" name="numero" required min="0">
            </div>
            <div>
                <label for="descripcion">Descripción (opcional):</label>
                <textarea id="descripcion" name="descripcion" rows="3"></textarea>
            </div>
            <button type="submit">Crear Tarea</button>
        </form>

        <h2>Lista de Tareas</h2>
        <div id="task-list" class="task-list">
            <!-- Las tareas se cargarán aquí -->
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            fetchTasks();

            document.getElementById('task-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const titulo = document.getElementById('titulo').value;
                const numero = document.getElementById('numero').value;
                const descripcion = document.getElementById('descripcion').value;

                try {
                    const response = await fetch('/tareas', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ titulo, numero: parseInt(numero), descripcion })
                    });
                    const data = await response.json();
                    if (response.ok) {
                        alert('Tarea creada exitosamente!');
                        document.getElementById('task-form').reset();
                        fetchTasks();
                    } else {
                        alert('Error al crear tarea: ' + (data.error || 'Mensaje desconocido'));
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error de red o del servidor.');
                }
            });
        });

        async function fetchTasks() {
            try {
                const response = await fetch('/tareas');
                const tasks = await response.json();
                const taskListDiv = document.getElementById('task-list');
                taskListDiv.innerHTML = '';
                if (tasks.length === 0) {
                    taskListDiv.innerHTML = '<p>No hay tareas.</p>';
                } else {
                    tasks.forEach(task => {
                        const taskItem = document.createElement('div');
                        taskItem.className = `task-item ${task.estado.replace(' ', '-')}`;
                        taskItem.innerHTML = `
                            <div class="details">
                                <h3>${task.titulo} (ID: ${task.id})</h3>
                                <p><strong>Número Decimal:</strong> ${task.numero_decimal}</p>
                                <p><strong>Número Binario:</strong> ${task.numero_binario}</p>
                                ${task.descripcion ? `<p><strong>Descripción:</strong> ${task.descripcion}</p>` : ''}
                                <p><strong>Estado:</strong> <span id="estado-${task.id}">${task.estado}</span></p>
                                <p><small>Creada: ${task.fecha_creacion}</small></p>
                            </div>
                            <div class="actions">
                                <select class="status-select" onchange="updateTaskStatus(${task.id}, this.value)">
                                    <option value="pendiente" ${task.estado === 'pendiente' ? 'selected' : ''}>Pendiente</option>
                                    <option value="en progreso" ${task.estado === 'en progreso' ? 'selected' : ''}>En progreso</option>
                                    <option value="completado" ${task.estado === 'completado' ? 'selected' : ''}>Completado</option>
                                </select>
                                <button class="delete" onclick="deleteTask(${task.id})">Eliminar</button>
                            </div>
                        `;
                        taskListDiv.appendChild(taskItem);
                    });
                }
            } catch (error) {
                console.error('Error al cargar las tareas:', error);
                document.getElementById('task-list').innerHTML = '<p>Error al cargar las tareas.</p>';
            }
        }

        async function updateTaskStatus(id, newStatus) {
            try {
                const response = await fetch(`/tareas/${id}`, { // Ruta corregida aquí
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ estado: newStatus })
                });
                const data = await response.json();
                if (response.ok) {
                    alert('Estado de tarea actualizado!');
                    fetchTasks();
                } else {
                    alert('Error al actualizar estado: ' + (data.error || 'Mensaje desconocido'));
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error de red o del servidor.');
            }
        }

        async function deleteTask(id) {
            if (!confirm('¿Estás seguro de que quieres eliminar esta tarea?')) {
                return;
            }
            try {
                const response = await fetch(`/tareas/${id}`, { // Ruta corregida aquí
                    method: 'DELETE'
                });
                const data = await response.json();
                if (response.ok) {
                    alert('Tarea eliminada exitosamente!');
                    fetchTasks();
                } else {
                    alert('Error al eliminar tarea: ' + (data.error || 'Mensaje desconocido'));
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error de red o del servidor.');
            }
        }
    </script>
</body>
</html>
"""

# Rutas del backend

@app.route("/")
def home():
    """Ruta para la página principal que renderiza la plantilla HTML."""
    return render_template_string(HTML_TEMPLATE) # [1, 2]

@app.route('/tareas', methods=['POST'])
def crear_tarea():
    """Crea una nueva tarea con un título, número, descripción y estado inicial."""
    global contador_id # [3, 4]
    data = request.get_json(silent=True) # [3, 4]

    if not data: # [3, 4]
        return jsonify({"error": "El cuerpo de la solicitud debe ser JSON válido"}), 400 # [3, 4]

    titulo = data.get("titulo", "").strip() # [3, 4]
    numero = data.get("numero") # [3, 4]
    descripcion = data.get("descripcion", "") # [3, 4]

    if not titulo: # [3, 4]
        return jsonify({"error": "El título es obligatorio"}), 400 # [3, 4]
    if numero is None: # [3, 4]
        return jsonify({"error": "El campo 'numero' es obligatorio"}), 400 # [3, 4]

    try: # [3, 4]
        numero_int = int(numero) # [3, 4]
        if numero_int < 0: # [3, 4]
            return jsonify({"error": "El número debe ser un entero positivo"}), 400 # [3, 4]
    except (ValueError, TypeError): # [5, 6]
        return jsonify({"error": "El campo 'numero' debe ser un número entero válido"}), 400 # [5, 6]

    numero_binario = bin(numero_int)[2:] # [5, 6]
    tarea = { # [5, 6]
        "id": contador_id, # [5, 6]
        "titulo": titulo, # [5, 6]
        "numero_decimal": numero_int, # [5, 6]
        "numero_binario": numero_binario, # [5, 6]
        "descripcion": descripcion, # [5, 6]
        "estado": "pendiente", # [5, 6]
        "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S") # [5, 6]
    }

    tareas.append(tarea) # [5, 6]
    contador_id += 1 # [5, 6]
    return jsonify(tarea), 201 # [5, 6]

@app.route('/tareas', methods=['GET'])
def listar_tareas():
    """Lista todas las tareas existentes."""
    return jsonify(tareas), 200 # [7, 8]

@app.route('/tareas/<int:id_tarea>', methods=['PUT']) # RUTA CORREGIDA AQUÍ
def actualizar_estado(id_tarea):
    """Actualiza el estado de una tarea específica por su ID."""
    data = request.get_json(silent=True) # [7, 8]
    if not data: # [7, 8]
        return jsonify({"error": "El cuerpo de la solicitud debe ser JSON válido"}), 400 # [7, 8]

    nuevo_estado = data.get("estado") # [7, 8]
    if nuevo_estado not in ["pendiente", "en progreso", "completado"]: # [7, 8]
        return jsonify({"error": "El estado debe ser 'pendiente', 'en progreso' o 'completado'"}), 400 # [7, 8]

    tarea_encontrada = next((t for t in tareas if t["id"] == id_tarea), None) # [7, 8]

    if tarea_encontrada: # [9, 10]
        tarea_encontrada["estado"] = nuevo_estado # [9, 10]
        return jsonify(tarea_encontrada), 200 # [9, 10]
    return jsonify({"error": "Tarea no encontrada"}), 404 # [9, 10]

@app.route('/tareas/<int:id_tarea>', methods=['DELETE']) # RUTA CORREGIDA AQUÍ
def eliminar_tarea(id_tarea):
    """Elimina una tarea específica por su ID."""
    global tareas # [9, 10]
    tarea_original_len = len(tareas) # [9, 10]
    tareas = [t for t in tareas if t["id"] != id_tarea] # [9, 10]

    if len(tareas) < tarea_original_len: # [9, 10]
        return jsonify({"mensaje": "Tarea eliminada"}), 200 # [9, 10]
    return jsonify({"error": "Tarea no encontrada"}), 404 # [9, 10]

if __name__ == '__main__':
    app.run(debug=True) # [11, 12]