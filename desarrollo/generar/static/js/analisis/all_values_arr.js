document.addEventListener('DOMContentLoaded', function() {
    let miFormulario = document.getElementById('miFormulario');
    let btnPago = document.getElementById('btnPago');
    
    if (btnPago) {
        btnPago.addEventListener('click', function() {
            document.getElementById('miFormulario').addEventListener('submit', function(event) {
                event.preventDefault();
                
                var prueba = document.createElement('input');
                prueba.type = 'hidden';
                prueba.name = 'btnRespaldoPago';
                prueba.value = 4;
                document.getElementById('miFormulario').appendChild(prueba);

                Swal.fire({
                    title: "¿Seguro que el arrendatario ya pago?",
                    showDenyButton: true,
                    confirmButtonText: "Si",
                    denyButtonText: `No`
                  }).then((result) => {
                    /* Read more about isConfirmed, isDenied below */
                    if (result.isConfirmed) {
                      Swal.fire("Arrendatario actualizado!", "", "success").then((result) => {
                        if (result.isConfirmed) {
                            this.submit(); // Envía el formulario si el usuario confirma la acción
                        }});
                    } else if (result.isDenied) {
                      Swal.fire("No se guardaron los cambios", "", "info");
                    }
                  });
                })
            });
        };
    });
