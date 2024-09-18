document.addEventListener('DOMContentLoaded', function () {
    var propietarioButtons = document.querySelectorAll('[data-id]');
    var appliedDiscounts = {}; // Almacena los descuentos aplicados por inmueble
    var inmueblesSeleccionados = {}; // Almacena los valores por defecto de cada inmueble seleccionado

    function openModalWithContent(modal_pago) {
        fetch('/Analisis/All/ValuesPro/ConfirmarPago/' + modal_pago)
            .then(response => response.text())
            .then(data => {
                document.querySelector('#exampleModal .modal-body').innerHTML = data;
                var modal = new bootstrap.Modal(document.getElementById('exampleModal'));
                modal.show();
                setupCheckboxListeners();
                setupDescuentoSections();
            })
            .catch(error => {
                console.error('Error al cargar el contenido modal:', error);
            });
    }

    function calculateTotalWithDiscounts() {
        var total = 0;
        for (var inmuebleId in inmueblesSeleccionados) {
            var canon = inmueblesSeleccionados[inmuebleId];
            var descuento = appliedDiscounts[inmuebleId] || 0;
            total += (canon - descuento);
        }
        return total.toFixed(2);
    }

    function updateTotal() {
        var total = calculateTotalWithDiscounts();
        document.getElementById('totalPago').textContent = total;
        console.log('Total actualizado:', total);
    }

    function setupCheckboxListeners() {
        var checkboxes = document.querySelectorAll('.checkInmueble');
        checkboxes.forEach(function (checkbox) {
            checkbox.addEventListener('change', function () {
                var inmuebleId = checkbox.value;
                var canon = parseFloat(checkbox.getAttribute('data-canon'));
                var descuentoSection = document.querySelector('.descuentoSection[data-inmueble-id="' + inmuebleId + '"]');

                if (checkbox.checked) {
                    inmueblesSeleccionados[inmuebleId] = canon;
                    if (descuentoSection) {
                        descuentoSection.style.display = 'block';
                        descuentoSection.querySelector('.btnConfirmar').style.display = 'inline-block';
                        descuentoSection.querySelector('.btnCancelar').style.display = 'inline-block';
                    }
                } else {
                    delete inmueblesSeleccionados[inmuebleId];
                    resetDescuentos(inmuebleId);
                }
                updateTotal();
            });
        });
    }

    function setupDescuentoSections() {
        var btnConfirmar = document.querySelectorAll('.btnConfirmar');
        var btnCancelar = document.querySelectorAll('.btnCancelar');

        btnConfirmar.forEach(function (btn) {
            btn.addEventListener('click', function () {
                var inmuebleId = this.getAttribute('data-inmueble-id');
                aplicarDescuentos(inmuebleId);
            });
        });

        btnCancelar.forEach(function (btn) {
            btn.addEventListener('click', function () {
                var inmuebleId = this.getAttribute('data-inmueble-id');
                resetDescuentos(inmuebleId);
                updateTotal();
            });
        });
    }

    function aplicarDescuentos(inmuebleId) {
        var descuentoItems = document.querySelectorAll('.descuentoSection[data-inmueble-id="' + inmuebleId + '"] .descuento-item');
        var totalDescuento = 0;
        var descuentoIds = [];

        descuentoItems.forEach(function (item) {
            var valorDescuento = parseFloat(item.querySelector('.valor-descuento').textContent.replace('Valor: $', '').trim());
            var idDescuento = item.querySelector('.id-descuento').textContent.trim();
            if (!isNaN(valorDescuento)) {
                totalDescuento += valorDescuento;
                descuentoIds.push(idDescuento);
            }
        });

        appliedDiscounts[inmuebleId] = totalDescuento;
        updateTotal();

        document.getElementById('pConfirmacion_' + inmuebleId).style.display = 'block';
        document.querySelector('.descuentoSection[data-inmueble-id="' + inmuebleId + '"]').style.display = 'none';
        
        var idsDescuentosInput = document.createElement('input');
        idsDescuentosInput.type = 'hidden';
        idsDescuentosInput.name = 'idsDescuentos_' + inmuebleId;
        idsDescuentosInput.value = descuentoIds.join(',');
        document.getElementById('ModalPago').appendChild(idsDescuentosInput);
    }

    function resetDescuentos(inmuebleId) {
        appliedDiscounts[inmuebleId] = 0;
        document.getElementById('pConfirmacion_' + inmuebleId).style.display = 'none';
        document.querySelector('.descuentoSection[data-inmueble-id="' + inmuebleId + '"]').style.display = 'none';
        updateTotal();
    }

    propietarioButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            var propietarioId = this.getAttribute('data-id');
            openModalWithContent(propietarioId);
        });
    });

    document.getElementById('exampleModal').addEventListener('click', function (event) {
        if (event.target.classList.contains('actualizarM') && event.target.textContent === 'Pagar') {
            event.preventDefault();
            var modal = bootstrap.Modal.getInstance(document.getElementById('exampleModal'));
            modal.hide();
            var form = document.getElementById('ModalPago');
            var checkboxes = document.querySelectorAll('.checkInmueble:checked');

            checkboxes.forEach(function (checkbox) {
                var inmuebleId = checkbox.value;
                var hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'inmuebleIds[]';
                hiddenInput.value = inmuebleId;
                form.appendChild(hiddenInput);

                var descuento = appliedDiscounts[inmuebleId] || 0;
                var descuentoInput = document.createElement('input');
                descuentoInput.type = 'hidden';
                descuentoInput.name = 'descuentosAplicados_' + inmuebleId;
                descuentoInput.value = descuento;
                form.appendChild(descuentoInput);

                var totalPagoInput = document.createElement('input');
                totalPagoInput.type = 'hidden';
                totalPagoInput.name = 'totalPagar_' + inmuebleId;
                totalPagoInput.value = inmueblesSeleccionados[inmuebleId];
                form.appendChild(totalPagoInput);
            });

            form.submit();
        }
    });
});


