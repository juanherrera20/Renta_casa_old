document.addEventListener('DOMContentLoaded', function() {
    var btnDescuento = document.getElementById('btnDescuento');
    var btnConfirmar = document.getElementById('btnConfirmar');
    var btnCancelar = document.getElementById('btnCancelar');
    var miFormulario = document.getElementById('miFormulario');
    

    if(btnDescuento){
        btnDescuento.addEventListener('click', function() {
            var inputs = miFormulario.querySelectorAll('input[name="descuento"], input[name="descripcionDescuento"], input[name="docRespaldo"]');
            inputs.forEach(function(input) {
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
                input.setAttribute('required', '');
            });
            this.style.display = 'none';
            if (btnConfirmar) {
                btnConfirmar.style.display = 'block';
            }
            if (btnCancelar) {
                btnCancelar.style.display = 'block';
            }
    });
    };
    if (btnCancelar) {
        btnCancelar.addEventListener('click', function() {
            var inputs = miFormulario.querySelectorAll('input[name="descuento"], input[name="descripcionDescuento"], input[name="docRespaldo"]');
            inputs.forEach(function(input) {
                input.setAttribute('readonly', '');
                input.setAttribute('disabled', '');
                input.removeAttribute('required');
            });
            this.style.display = 'none';
            if (btnDescuento) {
                btnDescuento.style.display = 'block';
            }
            if (btnCancelar) {
                btnCancelar.style.display = 'none';
            }
            if (btnConfirmar) {
                btnConfirmar.style.display = 'none';
            }
        });
    }
    if (btnConfirmar) {
        btnConfirmar.addEventListener('click', function() {
            document.getElementById('miFormulario').addEventListener('submit', function(event) {
                event.preventDefault();
                var descuento = document.querySelector('input[name="descuento"]').value;
                var valorPago = document.querySelector('input[name="valor_pago"]').value;

                descuento = parseFloat(descuento);
                valorPago = parseFloat(valorPago);
                var nuevoTotal = valorPago - descuento;
                Swal.fire({
                    title: "Cambio de pago!",
                    text: "El valor de pago no es $"+valorPago+" sino $"+nuevoTotal,
                    icon: "success",
                    confirmButtonText: 'Ok'
                }).then((result) => {
                    if (result.isConfirmed) {
                        this.submit(); // Envía el formulario si el usuario confirma la acción
                    }
                });
            });
        });
    };
});
