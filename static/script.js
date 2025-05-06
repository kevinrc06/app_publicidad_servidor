$(document).ready(function () {
    let horariosRegistrados = []; // ← Aquí guardaremos los rangos horarios

    function actualizarListaImagenes() {
        $.get("/imagenes", function (data) {
            horariosRegistrados = []; // Limpiamos antes de volver a llenar

            let lista = $("#imagenesLista");
            lista.empty();

            data.forEach(img => {
                // Guardamos los horarios para validación futura
                horariosRegistrados.push({
                    inicio: img.horario_inicio,
                    fin: img.horario_fin
                });

                let item = `<li class="list-group-item d-flex justify-content-between align-items-center">
                    <div class="d-flex align-items-center">
                        <img src="/imagenes/${img.nombre}" class="img-thumbnail me-3" width="100">
                        <div>
                            <strong>${img.nombre}</strong><br>
                            <small>${img.horario_inicio} - ${img.horario_fin}</small>
                        </div>
                    </div>
                    <button class="btn btn-danger btn-sm" onclick="eliminarImagen('${img.nombre}')">Eliminar</button>
                </li>`;
                lista.append(item);
            });
        });
    }

    window.eliminarImagen = function (nombre) {
        Swal.fire({
            title: "¿Estás seguro?",
            text: "No podrás revertir esta acción.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar"
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: "/eliminar_imagen",
                    type: "POST",
                    contentType: "application/json",
                    data: JSON.stringify({ nombre: nombre }),
                    success: function (response) {
                        Swal.fire("¡Eliminado!", response.message, "success");
                        actualizarListaImagenes();
                    },
                    error: function () {
                        Swal.fire("Error", "Hubo un problema al eliminar la imagen.", "error");
                    }
                });
            }
        });
    };

    actualizarListaImagenes();

    $("#uploadForm").on("submit", function (event) {
        event.preventDefault();

        let file = $("#imageInput")[0].files[0];
        let horarioInicio = $("#horaInicio").val();
        let horarioFin = $("#horaFin").val();

        if (!file || !horarioInicio || !horarioFin) {
            Swal.fire("¡Error!", "Todos los campos son obligatorios.", "error");
            return;
        }

        /*/ Validación de rango lógico
        if (horarioInicio >= horarioFin) {
            Swal.fire("Horario inválido", "La hora de inicio debe ser menor que la hora de fin.", "warning");
            return;
        }*/

        // Validación de solapamiento
        let hayConflicto = horariosRegistrados.some(h => {
            return (
                (horarioInicio >= h.inicio && horarioInicio < h.fin) || // inicia dentro de otro
                (horarioFin > h.inicio && horarioFin <= h.fin) ||       // termina dentro de otro
                (horarioInicio <= h.inicio && horarioFin >= h.fin)      // lo cubre completamente
            );
        });

        if (hayConflicto) {
            Swal.fire("Conflicto de horario", "El horario se cruza con uno ya registrado.", "warning");
            return;
        }

        // Todo ok, enviar
        let formData = new FormData();
        formData.append("image", file);
        formData.append("horario_inicio", horarioInicio);
        formData.append("horario_fin", horarioFin);

        $.ajax({
            url: "/upload",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                Swal.fire("¡Éxito!", response.message, "success");
                $("#uploadForm")[0].reset();
                $("#imagePreview").attr("src", "").addClass("d-none");
                actualizarListaImagenes(); // esto actualizará también los horarios en memoria
            },
            error: function () {
                Swal.fire("Error", "Hubo un problema al subir la imagen.", "error");
            }
        });
    });
});
