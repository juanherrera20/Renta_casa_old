
  window.onload = function() {
    document.getElementById('buscar').addEventListener('input', function() {
      var value = this.value.toUpperCase();
      var rows = document.getElementById('propietarios').getElementsByTagName('tr');
      for (var i = 0; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName('td');
        var match = false;
        for (var j = 0; j < cells.length; j++) {
          if (cells[j].textContent.toUpperCase().indexOf(value) > -1) {
            match = true;
            break;
          }
        }
        rows[i].style.display = match ? "" : "none";
      }
    });
    document.getElementById('buscar1').addEventListener('input', function() {
        var value = this.value.toUpperCase();
        var rows = document.getElementById('inquilinos').getElementsByTagName('tr');
        for (var i = 0; i < rows.length; i++) {
          var cells = rows[i].getElementsByTagName('td');
          var match = false;
          for (var j = 0; j < cells.length; j++) {
            if (cells[j].textContent.toUpperCase().indexOf(value) > -1) {
              match = true;
              break;
            }
          }
          rows[i].style.display = match ? "" : "none";
        }
      });
      document.getElementById('buscar2').addEventListener('input', function() {
        var value = this.value.toUpperCase();
        var rows = document.getElementById('inmuebles').getElementsByTagName('tr');
        for (var i = 0; i < rows.length; i++) {
          var cells = rows[i].getElementsByTagName('td');
          var match = false;
          for (var j = 0; j < cells.length; j++) {
            if (cells[j].textContent.toUpperCase().indexOf(value) > -1) {
              match = true;
              break;
            }
          }
          rows[i].style.display = match ? "" : "none";
        }
      });
  };

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
});


