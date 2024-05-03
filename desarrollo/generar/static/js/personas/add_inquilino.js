document.addEventListener("DOMContentLoaded", function() {
    var label = document.getElementById("label");
    var select = document.getElementById("selectInmu");
    Swal.fire({
        title: "¿Quieres asignarle una propiedad?",
        showDenyButton: true,
        confirmButtonText: "Si!",
        denyButtonText: `No, después`
    }).then((result) => {
        if (result.isConfirmed) {
            if (label) {
                label.style.display = 'block';
            }
            if (select) {
                select.style.display = 'block';
                select.required = true;
            }
        } else if (result.isDenied) {
            Swal.fire("Recuerda que en 'inmueble' puedes agregar el arrendatario", "", "info");
        }
    });
    var form = document.getElementById('addInquilino');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        Swal.fire("Dato guardado con exito!", "", "success").then((result) => {
            if (result.isConfirmed) {
                this.submit(); // Envía el formulario si el usuario confirma la acción
            }
        });
    });
});