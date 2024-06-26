document.addEventListener('DOMContentLoaded', function() {
    var propietarioButtons = document.querySelectorAll('[data-id]');
    var appliedDiscounts = {};

    function openModalWithContent(modal_pago) {
        fetch('/Analisis/All/ValuesPro/ConfirmarPago/' + modal_pago)
            .then(response => response.text())
            .then(data => {
                document.querySelector('#exampleModal .modal-body').innerHTML = data;
                var modal = new bootstrap.Modal(document.getElementById('exampleModal'));
                modal.show();
                setupCheckboxListeners();  // Configura los listeners después de mostrar el modal
                setupDescuentoSections();  // Configura las secciones de descuento al abrir el modal
            })
            .catch(error => {
                console.error('Error al cargar el contenido modal:', error);
            });
    }

    function calculateTotalWithDiscounts() {
        var checkboxes = document.querySelectorAll('.checkInmueble:checked');
        var total = 0;
        checkboxes.forEach(function(checkbox) {
            var inmuebleId = checkbox.value;
            var canon = parseFloat(checkbox.getAttribute('data-canon'));
            var descuento = appliedDiscounts[inmuebleId] || 0; // Obtener el descuento aplicado o 0 si no hay
            total += (canon - descuento); // Restar el descuento del canon
        });
        return total.toFixed(2);
    }

    function updateTotal() {
        var total = calculateTotalWithDiscounts();
        document.getElementById('totalPago').textContent = total;
        console.log('Total actualizado:', total);  // Mensaje de consola para depuración
    }

    function setupCheckboxListeners() {
        var checkboxes = document.querySelectorAll('.checkInmueble');
        checkboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', function() {
                updateTotal();
                toggleDescuentoButton(checkbox);
                if (!checkbox.checked) {
                    // Si se deselecciona, restablecer el descuento
                    var inmuebleId = checkbox.value;
                    appliedDiscounts[inmuebleId] = 0;
                    ocultarMensaje(inmuebleId);
                }
            });
        });
    }

    function toggleDescuentoButton(checkbox) {
        var inmuebleId = checkbox.value;
        var btnDescuento = document.querySelector('.btnDescuento[data-inmueble-id="' + inmuebleId + '"]');
        if (checkbox.checked) {
            btnDescuento.style.display = 'inline-block';
        } else {
            btnDescuento.style.display = 'none';
            var descuentoSection = document.querySelector('.descuentoSection[data-inmueble-id="' + inmuebleId + '"]');
            if (descuentoSection) {
                descuentoSection.style.display = 'none';
                resetDescuentoFields(inmuebleId);
            }
        }
    }

    function setupDescuentoSections() {
        var btnDescuento = document.querySelectorAll('.btnDescuento');
        btnDescuento.forEach(function(btn) {
            btn.style.display = 'none';
        });

        var btnCancelar = document.querySelectorAll('.btnCancelar');
        var btnConfirmar = document.querySelectorAll('.btnConfirmar');

        btnDescuento.forEach(function(btn) {
            btn.addEventListener('click', function() {
                var inmuebleId = this.getAttribute('data-inmueble-id');
                var descuentoSection = document.querySelector('.descuentoSection[data-inmueble-id="' + inmuebleId + '"]');
                if (descuentoSection) {
                    descuentoSection.style.display = 'block';
                    enableDescuentoFields(inmuebleId);
                    this.style.display = 'none';
                    var btnCancelar = document.querySelector('.btnCancelar[data-inmueble-id="' + inmuebleId + '"]');
                    if (btnCancelar) {
                        btnCancelar.style.display = 'inline-block';
                    } else {
                        console.error('No se encontró el botón de cancelar para el inmueble con ID:', inmuebleId);
                    }
                    var btnConfirmar = document.querySelector('.btnConfirmar[data-inmueble-id="' + inmuebleId + '"]');
                    if (btnConfirmar) {
                        btnConfirmar.style.display = 'inline-block';
                    } else {
                        console.error('No se encontró el botón de confirmar descuento para el inmueble con ID:', inmuebleId);
                    }
                } else {
                    console.error('No se encontró la sección de descuento para el inmueble con ID:', inmuebleId);
                }
            });
        });

        btnCancelar.forEach(function(btn) {
            btn.addEventListener('click', function() {
                var inmuebleId = this.getAttribute('data-inmueble-id');
                var descuentoSection = document.querySelector('.descuentoSection[data-inmueble-id="' + inmuebleId + '"]');
                if (descuentoSection) {
                    descuentoSection.style.display = 'none';
                    disableDescuentoFields(inmuebleId);
                    var btnDescuento = document.querySelector('.btnDescuento[data-inmueble-id="' + inmuebleId + '"]');
                    if (btnDescuento) {
                        btnDescuento.style.display = 'inline-block';
                    } else {
                        console.error('No se encontró el botón de añadir descuento para el inmueble con ID:', inmuebleId);
                    }
                    var btnConfirmar = document.querySelector('.btnConfirmar[data-inmueble-id="' + inmuebleId + '"]');
                    if (btnConfirmar) {
                        btnConfirmar.style.display = 'none';
                    } else {
                        console.error('No se encontró el botón de confirmar descuento para cancelar para el inmueble con ID:', inmuebleId);
                    }
                } else {
                    console.error('No se encontró la sección de descuento para cancelar para el inmueble con ID:', inmuebleId);
                }
            });
        });

        btnConfirmar.forEach(function(btn) {
            btn.addEventListener('click', function() {
                var inmuebleId = this.getAttribute('data-inmueble-id');
                var descuentoInput = document.getElementById('descuento_' + inmuebleId);
                if (descuentoInput) {
                    var descuentoValue = parseFloat(descuentoInput.value);
                    if (isNaN(descuentoValue) || descuentoValue <= 0) {
                        Swal.fire({
                            title: "<strong>El valor de descuento debe ser mayor a 0 </strong>",
                            icon: "info",
                            confirmButtonText: `
                              <i class="fa fa-thumbs-up"></i> De acuerdo!
                            `,
                        });
                        return;
                    }
                    applyDiscount(inmuebleId, descuentoValue);
                } else {
                    console.error('No se encontró el input de descuento para el inmueble con ID:', inmuebleId);
                }
            });
        });
    }

    function enableDescuentoFields(inmuebleId) {
        // Habilitar campos de descuento
        document.getElementById('descuento_' + inmuebleId).removeAttribute('disabled');
        document.getElementById('descripcionDescuento_' + inmuebleId).removeAttribute('disabled');
        document.getElementById('docRespaldo_' + inmuebleId).removeAttribute('disabled');
    }

    function disableDescuentoFields(inmuebleId) {
        // Deshabilitar campos de descuento
        document.getElementById('descuento_' + inmuebleId).setAttribute('disabled', 'true');
        document.getElementById('descripcionDescuento_' + inmuebleId).setAttribute('disabled', 'true');
        document.getElementById('docRespaldo_' + inmuebleId).setAttribute('disabled', 'true');
    }

    function resetDescuentoFields(inmuebleId) {
        // Limpiar campos de descuento
        document.getElementById('descuento_' + inmuebleId).value = '';
        document.getElementById('descripcionDescuento_' + inmuebleId).value = '';
        document.getElementById('docRespaldo_' + inmuebleId).value = '';
        disableDescuentoFields(inmuebleId);
    }

    function applyDiscount(inmuebleId, descuento) {
        appliedDiscounts[inmuebleId] = descuento;
        updateTotal();

        // Ocultar botón de añadir descuento
        document.querySelector('.btnDescuento[data-inmueble-id="' + inmuebleId + '"]').style.display = 'none';
        // Mostrar mensaje de éxito
        document.getElementById('pConfirmacion_' + inmuebleId).style.display = 'block';
        // Ocultar la sección de descuento
        document.querySelector('.descuentoSection[data-inmueble-id="' + inmuebleId + '"]').style.display = 'none';
    }

    function ocultarMensaje(inmuebleId) {
        // Ocultar mensaje de éxito
        document.getElementById('pConfirmacion_' + inmuebleId).style.display = 'none';
    }

    // Modal
    document.querySelectorAll('.modal').forEach(function(modal) {
        modal.addEventListener('hidden.bs.modal', function() {
            document.body.style.overflow = 'auto';
            document.querySelector('.modal-backdrop').remove();
        });
    });

    propietarioButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var propietarioId = this.getAttribute('data-id');
            openModalWithContent(propietarioId);
        });
    });

    document.getElementById('exampleModal').addEventListener('click', function(event) {
        if (event.target.classList.contains('actualizarM') && event.target.textContent === 'Pagar') {
            // Enviar los datos a la vista para el procesamiento
            var form = document.getElementById('ModalPago');
            var checkboxes = document.querySelectorAll('.checkInmueble:checked');
            checkboxes.forEach(function(checkbox) {
                var inmuebleId = checkbox.value;
                var hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'inmuebleIds[]';
                hiddenInput.value = inmuebleId;
                form.appendChild(hiddenInput);

                var descuento = appliedDiscounts[inmuebleId] || 0;
                var descuentoInput = document.createElement('input');
                descuentoInput.type = 'hidden';
                descuentoInput.name = 'descuentos[]';
                descuentoInput.value = descuento;
                form.appendChild(descuentoInput);
            });
            form.submit();
        }
    });
});



    // if (btnPagar) {
    //     btnPagar.addEventListener('click', function() {
    //         document.getElementById('miFormulario').addEventListener('submit', function(event) {
    //             event.preventDefault();

    //             var prueba = document.createElement('input');
    //             prueba.type = 'hidden';
    //             prueba.name = 'btnRespaldoPagar';
    //             prueba.value = 4;
    //             document.getElementById('miFormulario').appendChild(prueba);

    //             Swal.fire({
    //                 title: "¿Seguro que quiere pagar?",
    //                 showDenyButton: true,
    //                 confirmButtonText: "Si",
    //                 denyButtonText: `No`
    //               }).then((result) => {
    //                 /* Read more about isConfirmed, isDenied below */
    //                 if (result.isConfirmed) {
    //                   Swal.fire("Propietario pagado!", "", "success").then((result) => {
    //                     if (result.isConfirmed) {
    //                         this.submit(); // Envía el formulario si el usuario confirma la acción
    //                     }});
    //                 } else if (result.isDenied) {
    //                   Swal.fire("Propietario no actualizado", "", "info");
    //                 }
    //               });
    //             })
    //         });
    //     };
    // });

    
    

    // if (btnPagar) {
    //     btnPagar.addEventListener('click', function() {
    //         document.getElementById('miFormulario').addEventListener('submit', function(event) {
    //             event.preventDefault();

    //             var prueba = document.createElement('input');
    //             prueba.type = 'hidden';
    //             prueba.name = 'btnRespaldoPagar';
    //             prueba.value = 4;
    //             document.getElementById('miFormulario').appendChild(prueba);

    //             Swal.fire({
    //                 title: "¿Seguro que quiere pagar?",
    //                 showDenyButton: true,
    //                 confirmButtonText: "Si",
    //                 denyButtonText: `No`
    //               }).then((result) => {
    //                 /* Read more about isConfirmed, isDenied below */
    //                 if (result.isConfirmed) {
    //                   Swal.fire("Propietario pagado!", "", "success").then((result) => {
    //                     if (result.isConfirmed) {
    //                         this.submit(); // Envía el formulario si el usuario confirma la acción
    //                     }});
    //                 } else if (result.isDenied) {
    //                   Swal.fire("Propietario no actualizado", "", "info");
    //                 }
    //               });
    //             })
    //         });
    //     };
    // });

    
    