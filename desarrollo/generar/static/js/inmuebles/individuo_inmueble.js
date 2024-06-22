document.addEventListener('DOMContentLoaded', function() {
    var btnEdit = document.getElementById('btnEdit');
    var btnCancel = document.getElementById('btnCancel');
    var btnActualizar = document.getElementById('btnActualizar');
    var miFormulario = document.getElementById('miFormulario');
    var imagenInput = document.getElementById('imagenInput');
    var documentoInput = document.getElementById('documentoInput');
    var addArrendatario = document.getElementById('addArrendatario');
    var arrendatarioTitle = document.getElementById('arrendatarioTitle');
    var addPropietario = document.getElementById('addPropietario');
    var pripietarioTitle = document.getElementById('pripietarioTitle');

    if (btnEdit) {
        btnEdit.addEventListener('click', function() {
            var inputs = miFormulario.querySelectorAll('input, select');
            inputs.forEach(function(input) {
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
            });

            // Cambiar el tipo de input de 'fecha_pago' a 'date' y almacenar el valor original
            var fechaPagoInput = miFormulario.querySelector('input[name="fechaPago"]');
            if (fechaPagoInput) {
                fechaPagoInput.dataset.originalValue = fechaPagoInput.value; // Almacenar el valor original
                fechaPagoInput.type = 'date';
            }

            this.style.display = 'none';
            if (btnActualizar) {
                btnActualizar.style.display = 'block';
            }
            if (btnCancel) {
                btnCancel.style.display = 'block';
            }
            if (imagenInput) {
                imagenInput.style.display = 'block';
            }
            if (documentoInput) {
                documentoInput.style.display = 'block';
            }
            if (addArrendatario) {
                addArrendatario.style.display = 'block';
            }
            if (arrendatarioTitle) {
                arrendatarioTitle.style.display = 'block';  
            }
            if (addPropietario) {
                addPropietario.style.display = 'block';  
            }
            if (pripietarioTitle) {
                pripietarioTitle.style.display = 'block';  
            }
            
        });
    }

    if (btnCancel) {
        btnCancel.addEventListener('click', function() {
            location.reload(); // Recargar la página para descartar los cambios
            // var inputs = miFormulario.querySelectorAll('input, select');
            // inputs.forEach(function(input) {
            //     input.setAttribute('readonly', '');
            //     input.setAttribute('disabled', '');
            // });

            // // Cambiar el tipo de input de 'fecha_pago' de nuevo a 'datetime' y restaurar el valor original
            // var fechaPagoInput = miFormulario.querySelector('input[name="fecha_pago"]');
            // if (fechaPagoInput) {
            //     fechaPagoInput.type = 'datetime';
            //     fechaPagoInput.value = fechaPagoInput.dataset.originalValue; // Restaurar el valor original
            // }

            // this.style.display = 'none';
            // if (btnEdit) {
            //     btnEdit.style.display = 'block';
            // }
            // if (imagenInput) {
            //     imagenInput.style.display = 'none';
            // }
            // if (documentoInput) {
            //     documentoInput.style.display = 'none';
            // }
            // if (addArrendatario) {
            //     addArrendatario.style.display = 'none';
            // }
            // if (arrendatarioTitle) {
            //     arrendatarioTitle.style.display = 'none';  
            // }
            // if (addPropietario) {
            //     addPropietario.style.display = 'none';  
            // }
            // if (pripietarioTitle) {
            //     pripietarioTitle.style.display = 'none';  
            // }
            
        });
    }
    
});