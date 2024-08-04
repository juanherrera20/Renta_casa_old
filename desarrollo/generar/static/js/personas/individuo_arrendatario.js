document.addEventListener('DOMContentLoaded', function() {
    var btnEdit = document.getElementById('btnEdit');
    var btnCancel = document.getElementById('btnCancel');
    var btnActualizar = document.getElementById('btnActualizar');
    var miFormulario = document.getElementById('miFormulario');
    var Label = document.getElementById('LabelFechaFin');
    var label2 = document.getElementById('LabelFinContrato');

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
                finContratoInput.type = 'hidden';
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
            if (label2) {
                label2.style.display = 'none';
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
                fechaPagoInput.type = 'date';
                fechaPagoInput.value = fechaPagoInput.dataset.originalValue; 
            }
            var inicioContratoInput = miFormulario.querySelector('input[name="inicio_contrato"]');
            if (inicioContratoInput) {
                inicioContratoInput.type = 'date';
                inicioContratoInput.value = inicioContratoInput.dataset.originalValue;
            }
            var finContratoInput = miFormulario.querySelector('input[name="fin_contrato"]');
            if (finContratoInput) {
                finContratoInput.type = 'date';
                finContratoInput.value = finContratoInput.dataset.originalValue; // Restaurar el valor original
            }
            var fechaLimiteInput = miFormulario.querySelector('input[name="fecha_fin"]');
            if (fechaLimiteInput) {
                fechaLimiteInput.type = 'date';
                fechaLimiteInput.value = fechaLimiteInput.dataset.originalValue;
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
            if (label2) {
                label2.style.display = 'block';
            }  
        });
    }
    miFormulario.addEventListener('submit', function(event) {
        event.preventDefault();
        Swal.fire("Dato actualizado con exito!", "", "success").then((result) => {
            if (result.isConfirmed) {
                this.submit(); // Envía el formulario si el usuario confirma la acción
            }
        });
    });
});