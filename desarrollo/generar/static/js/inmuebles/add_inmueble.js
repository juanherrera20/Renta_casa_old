document.addEventListener("DOMContentLoaded", function() {
    var form = document.getElementById('addInmueble');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        Swal.fire("Inmueble guardado con exito!", "", "success").then((result) => {
            if (result.isConfirmed) {
                this.submit(); // Envía el formulario si el usuario confirma la acción
            }
        });
    });
});