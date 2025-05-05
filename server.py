from flask import Flask, send_file , request, jsonify, render_template, send_from_directory
import os
import zipfile

app = Flask(__name__, template_folder="templates")


# Ruta donde están las imágenes
IMAGES_FOLDER = "imagenes"
ZIP_FILE = "imagenes.zip"
METADATA_FILE = "horarios.txt"

HORARIOS_IMAGENES = {}

if not os.path.exists(IMAGES_FOLDER):
    os.makedirs(IMAGES_FOLDER)


def cargar_horarios():
    """Carga los horarios desde el archivo horarios.txt si existe."""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            for linea in f:
                datos = linea.strip().split(",")
                if len(datos) == 3:
                    imagen, hora_inicio, hora_fin = datos
                    HORARIOS_IMAGENES[imagen] = (hora_inicio, hora_fin)

# 🟢 Guardar horarios cuando se sube una imagen o se elimina
def guardar_horarios():
    """Guarda los horarios en un archivo de texto."""
    with open(METADATA_FILE, "w") as f:
        for imagen, (hora_inicio, hora_fin) in HORARIOS_IMAGENES.items():
            f.write(f"{imagen},{hora_inicio},{hora_fin}\n")

# 🔄 Cargar horarios al iniciar
cargar_horarios()

@app.route('/')
def index():
    print("Se ha llamado a la ruta /")  # Debug
    return render_template('index.html')



@app.route('/imagenes/<filename>')
def get_image(filename):
    return send_from_directory(IMAGES_FOLDER, filename)



@app.route('/imagenes', methods=['GET'])
def listar_imagenes():
    """Devuelve la lista de imágenes y sus horarios."""
    imagenes = [
        {"nombre": nombre, "horario_inicio": horario[0], "horario_fin": horario[1]}
        for nombre, horario in HORARIOS_IMAGENES.items()
    ]
    return jsonify(imagenes)


@app.route('/upload', methods=['POST'])
def upload_image():
    """Recibe una imagen y sus horarios, y la guarda en la carpeta de imágenes."""
    if 'image' not in request.files:
        return jsonify({"error": "No se envió ninguna imagen"}), 400

    file = request.files['image']
    horario_inicio = request.form['horario_inicio']
    horario_fin = request.form['horario_fin']

    if file.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    file_path = os.path.join(IMAGES_FOLDER, file.filename)
    file.save(file_path)
    HORARIOS_IMAGENES[file.filename] = (horario_inicio, horario_fin)
    guardar_horarios()


    return jsonify({"message": f"Imagen {file.filename} subida con éxito"}), 200





def create_zip():
    """Crea un archivo ZIP con todas las imágenes de la carpeta IMAGES_FOLDER."""
    
    guardar_horarios()

    with zipfile.ZipFile(ZIP_FILE, 'w', zipfile.ZIP_DEFLATED) as zipf:

        zipf.write(METADATA_FILE)


        for imagen in HORARIOS_IMAGENES.keys():
            file_path = os.path.join(IMAGES_FOLDER, imagen)
            zipf.write(file_path, os.path.relpath(file_path, IMAGES_FOLDER))

@app.route('/eliminar_imagen', methods=['POST'])
def eliminar_imagen():
    """Elimina una imagen y la borra del archivo de horarios."""
    data = request.get_json()
    nombre_imagen = data.get("nombre")

    if nombre_imagen in HORARIOS_IMAGENES:
        file_path = os.path.join(IMAGES_FOLDER, nombre_imagen)
        if os.path.exists(file_path):
            os.remove(file_path)

        del HORARIOS_IMAGENES[nombre_imagen]
        guardar_horarios()  # Actualizar archivo de horarios
        return jsonify({"message": f"Imagen {nombre_imagen} eliminada"}), 200

    return jsonify({"error": "Imagen no encontrada"}), 404



@app.route('/download')
def download_zip():
    """Genera y envía el archivo ZIP al usuario."""
    create_zip()
    return send_file(ZIP_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
