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
