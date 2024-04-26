document.addEventListener('DOMContentLoaded', function() {
    // Obtén todos los botones de tarea
    var tareaButtons = document.querySelectorAll('[data-id]');

    // Función para abrir el modal y cargar el contenido dinámico
    function openModalWithContent(modal_ver_tarea) {
        fetch('Modal/' + modal_ver_tarea)
            .then(response => response.text())
            .then(data => {
                document.querySelector('#exampleModal .modal-body').innerHTML = data;
                // Abre el modal
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
        if (event.target.classList.contains('actualizarM') && event.target.textContent === 'Actualizar') {
          // Submit the form programmatically if clicked
          document.getElementById('form_modal').submit();
        }
      });
});
