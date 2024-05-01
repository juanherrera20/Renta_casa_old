document.addEventListener('DOMContentLoaded', function() {
    var btnEdit = document.getElementById('btnEdit');
    var btnCancel = document.getElementById('btnCancel');
    var btnActualizar = document.getElementById('btnActualizar');
    var miFormulario = document.getElementById('miFormulario');
    var Label = document.getElementById('LabelFechaFin');

    if (btnEdit) {
        btnEdit.addEventListener('click', function() {
            var inputs = miFormulario.querySelectorAll('input, select');
            inputs.forEach(function(input) {
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
            });
            var fechaPagoInput = miFormulario.querySelector('input[name="fecha_inicio"]');
            if (fechaPagoInput) {
                fechaPagoInput.dataset.originalValue = fechaPagoInput.value;
                fechaPagoInput.type = 'date';
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
        });
    }

    if (btnCancel) {
        btnCancel.addEventListener('click', function() {
            var inputs = miFormulario.querySelectorAll('input, select');
            inputs.forEach(function(input) {
                input.setAttribute('readonly', '');
                input.setAttribute('disabled', '');
            });
            var fechaPagoInput = miFormulario.querySelector('input[name="fecha_inicio"]');
            if (fechaPagoInput) {
                fechaPagoInput.type = 'datetime';
                fechaPagoInput.value = fechaPagoInput.dataset.originalValue; 
            }
            var inicioContratoInput = miFormulario.querySelector('input[name="inicio_contrato"]');
            if (inicioContratoInput) {
                inicioContratoInput.type = 'datetime';
                inicioContratoInput.value = inicioContratoInput.dataset.originalValue;
            }
            var finContratoInput = miFormulario.querySelector('input[name="fin_contrato"]');
            if (finContratoInput) {
                finContratoInput.type = 'datetime';
                finContratoInput.value = finContratoInput.dataset.originalValue; // Restaurar el valor original
            }
            var fechaLimiteInput = miFormulario.querySelector('input[name="fecha_fin"]');
            if (fechaLimiteInput) {
                fechaLimiteInput.type = 'datetime';
                fechaLimiteInput.value = finContratoInput.dataset.originalValue;
            }
            this.style.display = 'none';
            if (btnEdit) {
                btnEdit.style.display = 'block';
            }
            if (btnActualizar) {
                btnActualizar.style.display = 'none';
            }
            if (Label) {
                Label.style.display = 'block';
            }  
        });
    }
});