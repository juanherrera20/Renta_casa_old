document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('registration').addEventListener('submit', function(event) {
        event.preventDefault(); // Evita que el formulario se envíe normalmente
        Swal.fire({
            title: "Excelente!",
            text: "Usuario guardado con éxito!",
            icon: "success",
            confirmButtonText: 'Ok'
        }).then((result) => {
            if (result.isConfirmed) {
                this.submit(); // Envía el formulario si el usuario confirma la acción
            }
        });
    });
});
