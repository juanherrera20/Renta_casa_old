document.addEventListener('DOMContentLoaded', function() {
    var btnEdit = document.getElementById('btnEdit');
    var btnCancel = document.getElementById('btnCancel');
    var btnActualizar = document.getElementById('btnActualizar');
    var miFormulario = document.getElementById('miFormulario');

    if (btnEdit) {
        btnEdit.addEventListener('click', function() {
            var inputs = miFormulario.querySelectorAll('input, select');// Hacer todos los campos editables
            inputs.forEach(function(input) {
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
            });
            this.style.display = 'none';// Oculta el botón "Edit" y mostrar el botón "Actualizar" y "Cancelar"
            if (btnActualizar) {
                btnActualizar.style.display = 'block';
            }
            if (btnCancel) {
                btnCancel.style.display = 'block';
            }
        });
    }

    if (btnCancel) {
        btnCancel.addEventListener('click', function() {
            var inputs = miFormulario.querySelectorAll('input, select');// Volver a establecer todo
            inputs.forEach(function(input) {
                input.setAttribute('readonly', '');
                input.setAttribute('disabled', '');
            });            
            this.style.display = 'none';// Ocultar el botón "Cancelar" y mostrar el botón "Edit"
            if (btnEdit) {
                btnEdit.style.display = 'block';
            }
            if (btnActualizar) {
                btnActualizar.style.display = 'none';
            }
        });
    }
});