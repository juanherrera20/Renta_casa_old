document.addEventListener('DOMContentLoaded', function() {
    // Variables
    let btnPago = document.getElementById('btnPago');
    let btnDescuento = document.querySelector('.btnDescuento');
    let btnConfirmar = document.querySelector('.btnConfirmar');
    let btnCancelar = document.querySelector('.btnCancelar');
    let descuentoInput = document.getElementById('descuento');
    let descripcionInput = document.getElementById('descripcionDescuento');
    let docRespaldoInput = document.getElementById('docRespaldo');
    let valorTotalInput = document.querySelector('input[name="valor_total"]');
    let pConfirmacion = document.getElementById('pConfirmacion');
    let descuentoContainer = document.getElementById('descuento-container');

    // Verificar si el elemento de valor total existe
    if (!valorTotalInput) {
        console.error('El elemento con name "valor_total" no se encontró.');
        return;
    }

    // Obtener el valor original del total y eliminar el símbolo `$`
    let valorTotalOriginal = parseFloat(valorTotalInput.value.replace(/[^0-9.-]+/g, "")) || 0;

    // Ocultar el botón de cancelar por defecto al cargar la página
    btnCancelar.style.display = 'none';

    // Evento para el botón de Pago
    if (btnPago) {
        btnPago.addEventListener('click', function(event) {
            event.preventDefault();

            var prueba = document.createElement('input');
            prueba.type = 'hidden';
            prueba.name = 'btnRespaldoPago';
            prueba.value = 4;
            document.getElementById('miFormulario').appendChild(prueba);

            Swal.fire({
                title: "¿Seguro que el arrendatario ya pagó?",
                showDenyButton: true,
                confirmButtonText: "Sí",
                denyButtonText: `No`
            }).then((result) => {
                if (result.isConfirmed) {
                    Swal.fire("Arrendatario actualizado!", "", "success").then((result) => {
                        if (result.isConfirmed) {
                            document.getElementById('miFormulario').submit(); // Envía el formulario si el usuario confirma la acción
                        }
                    });
                } else if (result.isDenied) {
                    Swal.fire("No se guardaron los cambios", "", "info");
                }
            });
        });
    }

    // Evento para el botón de Añadir Descuento
    if (btnDescuento) {
        btnDescuento.addEventListener('click', function() {
            // Mostrar los campos de descuento y ocultar el botón de añadir
            descuentoContainer.style.display = 'flex';
            btnConfirmar.style.display = 'inline-block';
            btnDescuento.style.display = 'none';
            pConfirmacion.style.display = 'none';

            // Habilitar los campos de descuento
            descuentoInput.disabled = false;
            descripcionInput.disabled = false;
            docRespaldoInput.disabled = false;
        });
    }

    // Evento para el botón de Cancelar
    if (btnCancelar) {
        btnCancelar.addEventListener('click', function() {
            // Ocultar los campos de descuento y mostrar el botón de añadir
            descuentoContainer.style.display = 'none';
            btnConfirmar.style.display = 'none';
            pConfirmacion.style.display = 'none';
            btnDescuento.style.display = 'inline-block';

            // Asegurarse de que el botón de cancelar esté oculto
            btnCancelar.style.display = 'none';

            // Habilitar los campos de descuento
            descuentoInput.disabled = true;
            descripcionInput.disabled = true;
            docRespaldoInput.disabled = true;

            // Restablecer el valor original del total
            valorTotalInput.value = `$ ${valorTotalOriginal.toFixed(2)}`;
        });
    }

    // Evento para el botón de Confirmar
    if (btnConfirmar) {
        btnConfirmar.addEventListener('click', function() {
            // Obtener el valor del descuento
            let descuento = parseFloat(descuentoInput.value) || 0;

            // Validar que el descuento no sea mayor que el total original
            if (descuento > valorTotalOriginal) {
                Swal.fire({
                    title: 'El descuento no puede ser mayor que el total',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
                return;
            }

            // Calcular el total final
            let totalFinal = valorTotalOriginal - descuento;
            valorTotalInput.value = `$ ${totalFinal.toFixed(2)}`;

            // Ocultar los campos de descuento y el botón de confirmar
            descuentoContainer.style.display = 'none';
            btnConfirmar.style.display = 'none';

            // Mostrar el mensaje de confirmación y el botón de cancelar
            pConfirmacion.style.display = 'block';
            btnCancelar.style.display = 'inline-block';

            // Aplicar efecto visual
            descuentoContainer.classList.add('descuento-highlight');
            setTimeout(() => {
                descuentoContainer.classList.remove('descuento-highlight');
            }, 2000);

        });
    }
});
