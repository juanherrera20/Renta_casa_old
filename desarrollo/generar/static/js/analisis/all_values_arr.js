document.addEventListener('DOMContentLoaded', function() {
    // Variables
    let btnPago = document.getElementById('btnPago');
    let btnPago2 = document.getElementById('btnPago2');
    let btnDescuento = document.querySelector('.btnDescuento');
    let btnOtroValor = document.querySelector('.btnOtroValor');
    let btnConfirmarDescuento = document.querySelector('.btnConfirmar');
    let btnConfirmarOtroValor = document.querySelector('.btnConfirmarOtroValor');
    let btnCancelarDescuento = document.querySelector('.btnCancelar');
    let btnCancelarOtroValor = document.querySelector('.btnCancelarOtroValor');
    let descuentoInput = document.getElementById('descuento');
    let otroValorInput = document.getElementById('otroValor');
    let descripcionDescuentoInput = document.getElementById('descripcionDescuento');
    let descripcionOtroValorInput = document.getElementById('descripcionOtroValor');
    let docRespaldoInput = document.getElementById('docRespaldo');
    let valorTotalInput = document.querySelector('input[name="valor_total"]');
    let pConfirmacionDescuento = document.getElementById('pConfirmacion');
    let pConfirmacionOtroValor = document.getElementById('pConfirmacionOtroValor');
    let descuentoContainer = document.getElementById('descuento-container');
    let otroValorContainer = document.getElementById('otro-valor-container');

    // Verificar si el elemento de valor total existe
    if (!valorTotalInput) {
        console.error('El elemento con name "valor_total" no se encontró.');
        return;
    }

    // Obtener el valor original del total y eliminar el símbolo `$`
    let valorTotalOriginal = parseFloat(valorTotalInput.value.replace(/[^0-9.-]+/g, "")) || 0;
    let valorTotalActual = valorTotalOriginal; // Valor total que se va actualizando

    // Ocultar los botones de cancelar por defecto al cargar la página
    btnCancelarDescuento.style.display = 'none';
    btnCancelarOtroValor.style.display = 'none';

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

      // Evento para el botón de Pago
      if (btnPago2) {
        btnPago2.addEventListener('click', function(event) {
            event.preventDefault();

            var prueba = document.createElement('input');
            prueba.type = 'hidden';
            prueba.name = 'btnRespaldoPago';
            prueba.value = 5;
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
            btnConfirmarDescuento.style.display = 'inline-block';
            btnDescuento.style.display = 'none';
            pConfirmacionDescuento.style.display = 'none';

            // Habilitar los campos de descuento
            descuentoInput.disabled = false;
            descripcionDescuentoInput.disabled = false;
            docRespaldoInput.disabled = false;
        });
    }

    // Evento para el botón de Añadir Otro Valor
    if (btnOtroValor) {
        btnOtroValor.addEventListener('click', function() {
            // Mostrar los campos de otro valor y ocultar el botón de añadir
            otroValorContainer.style.display = 'flex';
            btnConfirmarOtroValor.style.display = 'inline-block';
            btnOtroValor.style.display = 'none';
            pConfirmacionOtroValor.style.display = 'none';

            // Habilitar los campos de otro valor
            otroValorInput.disabled = false;
            descripcionOtroValorInput.disabled = false;
        });
    }

    // Evento para el botón de Cancelar Descuento
    if (btnCancelarDescuento) {
        btnCancelarDescuento.addEventListener('click', function() {
            // Ocultar los campos de descuento y mostrar el botón de añadir
            descuentoContainer.style.display = 'none';
            btnConfirmarDescuento.style.display = 'none';
            pConfirmacionDescuento.style.display = 'none';
            btnDescuento.style.display = 'inline-block';

            // Asegurarse de que el botón de cancelar esté oculto
            btnCancelarDescuento.style.display = 'none';

            // Deshabilitar los campos de descuento
            descuentoInput.disabled = true;
            descripcionDescuentoInput.disabled = true;
            docRespaldoInput.disabled = true;

            // Restablecer el valor actual del total sin el descuento
            valorTotalActual += parseFloat(descuentoInput.value) || 0;
            valorTotalInput.value = `$ ${valorTotalActual.toFixed(2)}`;
        });
    }

    // Evento para el botón de Cancelar Otro Valor
    if (btnCancelarOtroValor) {
        btnCancelarOtroValor.addEventListener('click', function() {
            // Ocultar los campos de otro valor y mostrar el botón de añadir
            otroValorContainer.style.display = 'none';
            btnConfirmarOtroValor.style.display = 'none';
            pConfirmacionOtroValor.style.display = 'none';
            btnOtroValor.style.display = 'inline-block';

            // Asegurarse de que el botón de cancelar esté oculto
            btnCancelarOtroValor.style.display = 'none';

            // Deshabilitar los campos de otro valor
            otroValorInput.disabled = true;
            descripcionOtroValorInput.disabled = true;

            // Restablecer el valor actual del total sin el otro valor
            valorTotalActual -= parseFloat(otroValorInput.value) || 0;
            valorTotalInput.value = `$ ${valorTotalActual.toFixed(2)}`;
        });
    }

    // Evento para el botón de Confirmar Descuento
    if (btnConfirmarDescuento) {
        btnConfirmarDescuento.addEventListener('click', function() {
            // Obtener el valor del descuento
            let descuento = parseFloat(descuentoInput.value) || 0;

            // Validar que el descuento no sea mayor que el total actual
            if (descuento > valorTotalActual) {
                Swal.fire({
                    title: 'El descuento no puede ser mayor que el total',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
                return;
            }

            // Calcular el total final
            valorTotalActual -= descuento;
            valorTotalInput.value = `$ ${valorTotalActual.toFixed(2)}`;

            // Ocultar los campos de descuento y el botón de confirmar
            descuentoContainer.style.display = 'none';
            btnConfirmarDescuento.style.display = 'none';

            // Mostrar el mensaje de confirmación y el botón de cancelar
            pConfirmacionDescuento.style.display = 'block';
            btnCancelarDescuento.style.display = 'inline-block';

            // Aplicar efecto visual
            descuentoContainer.classList.add('descuento-highlight');
            setTimeout(() => {
                descuentoContainer.classList.remove('descuento-highlight');
            }, 2000);
        });
    }

    // Evento para el botón de Confirmar Otro Valor
    if (btnConfirmarOtroValor) {
        btnConfirmarOtroValor.addEventListener('click', function() {
            // Obtener el valor del otro valor
            let otroValor = parseFloat(otroValorInput.value) || 0;

            // Calcular el total final
            valorTotalActual += otroValor;
            valorTotalInput.value = `$ ${valorTotalActual.toFixed(2)}`;

            // Ocultar los campos de otro valor y el botón de confirmar
            otroValorContainer.style.display = 'none';
            btnConfirmarOtroValor.style.display = 'none';

            // Mostrar el mensaje de confirmación y el botón de cancelar
            pConfirmacionOtroValor.style.display = 'block';
            btnCancelarOtroValor.style.display = 'inline-block';

            // Aplicar efecto visual
            otroValorContainer.classList.add('descuento-highlight');
            setTimeout(() => {
                otroValorContainer.classList.remove('descuento-highlight');
            }, 2000);
        });
    }
});