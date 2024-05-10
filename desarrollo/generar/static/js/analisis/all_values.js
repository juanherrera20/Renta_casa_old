document.addEventListener('DOMContentLoaded', function() {
    var btnEdit = document.getElementById('btnEdit');
    var btnCancel = document.getElementById('btnCancel');
    var btnActualizar = document.getElementById('btnActualizar');
    var btnDescuento = document.getElementById('btnDescuento');
    var btnConfirmar = document.getElementById('btnConfirmar');
    var btnCancelar = document.getElementById('btnCancelar');
    var Label = document.getElementById('LabelFechaFin');
    var imagenInput = document.getElementById('imagenInput');
    var documentoInput = document.getElementById('documentoInput');
    var addArrendatario = document.getElementById('addArrendatario');
    var arrendatarioTitle = document.getElementById('arrendatarioTitle');
    var addPropietario = document.getElementById('addPropietario');
    var pripietarioTitle = document.getElementById('pripietarioTitle');
    var miFormulario = document.getElementById('miFormulario');



    if(btnDescuento){
        btnDescuento.addEventListener('click', function() {
            var inputs = miFormulario.querySelectorAll('input[name="descuento"], input[name="descripcionDescuento"], input[name="docRespaldo"]');
            inputs.forEach(function(input) {
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
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


    if (btnEdit) {
        btnEdit.addEventListener('click', function() {
            var inputs = miFormulario.querySelectorAll('input, select');
            inputs.forEach(function(input) {
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
            });

            // Cambiar el tipo de input de 'fecha_pago' a 'date' y almacenar el valor original
            var fechaPagoInput = miFormulario.querySelector('input[name="fecha_pago"]');
            if (fechaPagoInput) {
                fechaPagoInput.dataset.originalValue = fechaPagoInput.value; // Almacenar el valor original
                fechaPagoInput.type = 'date';
            }
            var fechaPagoInput2 = miFormulario.querySelector('input[name="fecha_inicio"]');
            if (fechaPagoInput2) {
                fechaPagoInput2.dataset.originalValue = fechaPagoInput2.value;
                fechaPagoInput2.type = 'date';
            }
            var inicioContratoInput = miFormulario.querySelector('input[name="inicio_contrato"]');
            if (inicioContratoInput) {
                inicioContratoInput.dataset.originalValue = inicioContratoInput.value;
                inicioContratoInput.type = 'date';
            }
            var finContratoInput = miFormulario.querySelector('input[name="fin_contrato"]');
            if (finContratoInput) {
                finContratoInput.dataset.originalValue = finContratoInput.value;
                finContratoInput.type = 'date';
            }
            var fechaLimiteInput = miFormulario.querySelector('input[name="fecha_fin"]');
            if (fechaLimiteInput) {
                fechaLimiteInput.dataset.originalValue = fechaLimiteInput.value;
                fechaLimiteInput.type = 'hidden';
            }

            this.style.display = 'none';
            if (btnActualizar) {
                btnActualizar.style.display = 'block';
            }
            if (btnCancel) {
                btnCancel.style.display = 'block';
            }
            if (Label) {
                Label.style.display = 'none';
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
            var inputs = miFormulario.querySelectorAll('input, select');
            inputs.forEach(function(input) {
                input.setAttribute('readonly', '');
                input.setAttribute('disabled', '');
            });

            // Cambiar el tipo de input de 'fecha_pago' de nuevo a 'datetime' y restaurar el valor original
            var fechaPagoInput = miFormulario.querySelector('input[name="fecha_pago"]');
            if (fechaPagoInput) {
                fechaPagoInput.type = 'datetime';
                fechaPagoInput.value = fechaPagoInput.dataset.originalValue; // Restaurar el valor original
            }

            this.style.display = 'none';
            if (btnEdit) {
                btnEdit.style.display = 'block';
            }
            if (btnActualizar) {
                btnActualizar.style.display = 'none';
            }
            if (imagenInput) {
                imagenInput.style.display = 'none';
            }
            if (documentoInput) {
                documentoInput.style.display = 'none';
            }
            if (addArrendatario) {
                addArrendatario.style.display = 'none';
            }
            if (arrendatarioTitle) {
                arrendatarioTitle.style.display = 'none';  
            }
            if (addPropietario) {
                addPropietario.style.display = 'none';  
            }
            if (pripietarioTitle) {
                pripietarioTitle.style.display = 'none';  
            }
        });
    }
    
    if (btnCancelar) {
        btnCancelar.addEventListener('click', function() {
            var inputs = miFormulario.querySelectorAll('input[name="descuento"], input[name="descripcionDescuento"], input[name="docRespaldo"]');
            inputs.forEach(function(input) {
                input.setAttribute('readonly', '');
                input.setAttribute('disabled', '');
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


});
