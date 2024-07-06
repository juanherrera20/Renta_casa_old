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
  const buttons = document.querySelectorAll(".tarea-btn");
  buttons.forEach(button => {
    button.draggable = true;
    button.addEventListener("dragstart", (event) => {
      event.dataTransfer.setData('text/plain', button.dataset.id);
      button.classList.add("dragging"); // Add visual indicator
    });
    button.addEventListener("dragend", () => {
      button.classList.remove("dragging"); // Remove visual indicator
    });
  });
  const listaPendientes = document.querySelector('#lista-pendientes');
  const listaCompletas = document.querySelector('#lista-completas');
  const listaIncompletas = document.querySelector('#lista-incompletas');

  document.querySelectorAll('.lista-tareas').forEach(function(lista) {
    lista.addEventListener('dragover', event => {
      event.preventDefault(); // Permite la operación de soltar
      console.log('Elemento soltado en la lista');
    });
    lista.addEventListener('drop', event => {
      
      const taskId = event.dataTransfer.getData('text/plain');
      const tarea = document.querySelector(`[data-tarea-id="${taskId}"]`);

      if (lista === listaPendientes) {
        updateTaskStatus(taskId, 'Pendiente');
      } else if (lista === listaCompletas) {
        updateTaskStatus(taskId, 'Completa');
      } else if (lista === listaIncompletas) {
        updateTaskStatus(taskId, 'Incompleta');
      }
      lista.appendChild(tarea);
    });
  });
});
function updateTaskStatus(taskId, newStatus) {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  fetch('Estados/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({ taskId, newStatus }),
  })
 .then(response => {
    if (!response.ok) {
      throw new Error('Server responded with an error status: ' + response.status);
    }
    return response.json();
  })
 .then(data => {
    if (data.success) {
      console.log('Estado de la tarea actualizado exitosamente');
    } else {
      console.error('Error al actualizar el estado de la tarea');
    }
  })
 .catch(error => {
    console.error('Error:', error);
  });
}
/*   document.getElementById('exampleModal').addEventListener('click', function(event) {
  if (event.target.classList.contains('actualizarM') && event.target.textContent === 'Actualizar') {
    // Submit the form programmatically if clicked
    document.getElementById('form_modal').submit();
  }
}); */
function eliminarTarea(taskId) {
  fetch(`Eliminar-tarea/${taskId}/`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken') // Asegúrate de tener una función getCookie() que obtenga el token CSRF
    }
  })
 .then(response => response.json())
 .then(data => {
    if (data.success) {
      location.reload(); // Recarga la página para reflejar los cambios
    } else {
      alert('Hubo un error al eliminar la tarea.');
    }
  })
 .catch((error) => {
    console.error('Error:', error);
  });
}
