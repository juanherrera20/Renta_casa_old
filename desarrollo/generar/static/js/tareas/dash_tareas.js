document.addEventListener('DOMContentLoaded', function() {
  // Obtén todos los botones de tarea
  var tareaButtons = document.querySelectorAll('[data-id]');
  
  // Función para abrir el modal y cargar el contenido dinámico
  function openModalWithContent(modal_ver_tarea) {
  
      fetch('Modal/' + modal_ver_tarea)
          .then(response => response.text())
          .then(data => {
              // Suponiendo que la respuesta es el contenido HTML que quieres mostrar en el modal
              document.querySelector('#exampleModal .modal-body').innerHTML = data;
              // Abre el modal
              var modal = new bootstrap.Modal(document.getElementById('exampleModal'));
              
              modal.show();
          });
  }
  
  // Cerrar el modal y restablecer el fondo oscurecido
  function closeModalAndResetBackdrop() {
      var modalElement = document.querySelector('.modal.show');
      var bootstrapModal = bootstrap.Modal.getInstance(modalElement);
      bootstrapModal.hide();
      // Restablecer la pantalla de fondo
      document.querySelector('.modal-backdrop').remove();
  }
  
  document.querySelectorAll('.closeModal').forEach(function(button) {
      button.addEventListener('click', closeModalAndResetBackdrop);
  });
  
  // Escuchar el evento de cierre del modal para restablecer la pantalla de fondo
  document.querySelectorAll('.modal').forEach(function(modal) {
      modal.addEventListener('hidden.bs.modal', function() {
          // Restablecer la pantalla de fondo
          document.querySelector('.modal-backdrop').remove();
      });
  });
  
  tareaButtons.forEach(function(button) {
      button.addEventListener('click', function() {
          var tareaId = this.getAttribute('data-id');
          openModalWithContent(tareaId);
      });
  });
});
