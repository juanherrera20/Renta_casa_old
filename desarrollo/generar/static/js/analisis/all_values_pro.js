// modal_script.js
document.addEventListener('DOMContentLoaded', function() {
    var tareaButtons = document.querySelectorAll('[data-id]');

    function openModalWithContent(modal_pago) {
        fetch('Modal/' + modal_pago)
            .then(response => response.text())
            .then(data => {
                document.querySelector('#exampleModal .modal-body').innerHTML = data;
                var modal = new bootstrap.Modal(document.getElementById('exampleModal'));
                modal.show();
            });
    }

    document.querySelectorAll('.modal').forEach(function(modal) {
        modal.addEventListener('hidden.bs.modal', function() {
            document.body.style.overflow = 'auto';
            document.querySelector('.modal-backdrop').remove();
        });
    });

    tareaButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var tareaId = this.getAttribute('data-id');
            openModalWithContent(tareaId);
        });
    });

    document.getElementById('exampleModal').addEventListener('click', function(event) {
        if (event.target.classList.contains('actualizarM') && event.target.textContent === 'Pagar') {
            document.getElementById('ModalPago').submit();
        }
    });
});


// document.addEventListener('DOMContentLoaded', function() {
//     var btnDescuento = document.getElementById('btnDescuento');
//     var btnConfirmar = document.getElementById('btnConfirmar');
//     var btnCancelar = document.getElementById('btnCancelar');
//     var miFormulario = document.getElementById('miFormulario');
//     var btnPagar = document.getElementById('btnPagar')
    
    // if(btnDescuento){
    //     btnDescuento.addEventListener('click', function() {
    //         var inputs = miFormulario.querySelectorAll('input[name="descuento"], input[name="descripcionDescuento"], input[name="docRespaldo"]');
    //         inputs.forEach(function(input) {
    //             input.removeAttribute('readonly');
    //             input.removeAttribute('disabled');
    //             input.setAttribute('required', '');
    //         });
    //         this.style.display = 'none';
    //         if (btnConfirmar) {
    //             btnConfirmar.style.display = 'block';
    //         }
    //         if (btnCancelar) {
    //             btnCancelar.style.display = 'block';
    //         }
    // });
    // };
    // if (btnCancelar) {
    //     btnCancelar.addEventListener('click', function() {
    //         var inputs = miFormulario.querySelectorAll('input[name="descuento"], input[name="descripcionDescuento"], input[name="docRespaldo"]');
    //         inputs.forEach(function(input) {
    //             input.setAttribute('readonly', '');
    //             input.setAttribute('disabled', '');
    //             input.removeAttribute('required');
    //         });
    //         this.style.display = 'none';
    //         if (btnDescuento) {
    //             btnDescuento.style.display = 'block';
    //         }
    //         if (btnCancelar) {
    //             btnCancelar.style.display = 'none';
    //         }
    //         if (btnConfirmar) {
    //             btnConfirmar.style.display = 'none';
    //         }
    //     });
    // }
    // if (btnConfirmar) {
    //     btnConfirmar.addEventListener('click', function() {
    //         document.getElementById('miFormulario').addEventListener('submit', function(event) {
    //             event.preventDefault();
    //             var descuento = document.querySelector('input[name="descuento"]').value;
    //             var valorPago = document.querySelector('input[name="valor_pago"]').value;
                
    //             descuento = parseFloat(descuento);
    //             valorPago = parseFloat(valorPago);
    //             var nuevoTotal = valorPago - descuento;     

    //             var prueba = document.createElement('input');
    //             prueba.type = 'hidden';
    //             prueba.name = 'btnRespaldoConfirmar';
    //             prueba.value = 5;
    //             document.getElementById('miFormulario').appendChild(prueba);
    //             Swal.fire({
    //                 title: "Cambio de pago!",
    //                 text: "El valor de pago no es $"+valorPago+" sino $"+nuevoTotal,
    //                 icon: "success",
    //                 confirmButtonText: 'Ok'
    //             }).then((result) => {
    //                 if (result.isConfirmed) {
    //                     this.submit(); // Envía el formulario si el usuario confirma la acción
    //                 }
    //             });
    //         });
    //     });
    // };
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

    
    