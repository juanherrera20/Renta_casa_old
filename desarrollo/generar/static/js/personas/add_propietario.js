document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('addPropietario');
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Evita que el formulario se envíe normalmente
        
        Swal.fire({
            title: "¿Quiere asignarle una proiedad?",
            showDenyButton: true,
            showCancelButton: true,
            confirmButtonText: "Si",
            denyButtonText: `No, más tarde`
        }).then((result) => {
            if (result.isConfirmed) {
                // Serializar los datos del formulario
                var formData = new FormData(form);

                // Enviar los datos mediante AJAX
                fetch(form.action, {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Ocurrió un error al enviar el formulario.');
                    }
                    // Redireccionar después de enviar correctamente
                    window.location.href = "http://127.0.0.1:8000/AddInmuebles/";
                })
                .catch(error => {
                    console.error('Error:', error);
                    // Aquí puedes mostrar un mensaje de error al usuario si lo deseas
                });
            } else if (result.isDenied) {
                Swal.fire("Recuerda asignarle un inmueble.", "", "info").then((result) => {
                    if (result.isConfirmed) {
                        // Serializar los datos del formulario
                        var formData = new FormData(form);

                        // Enviar los datos mediante AJAX
                        fetch(form.action, {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Ocurrió un error al enviar el formulario.');
                            }
                            // No redireccionar en este caso, dejar al usuario en la misma página
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            // Aquí puedes mostrar un mensaje de error al usuario si lo deseas
                        });
                    }
                });
            }
        });
    });
});