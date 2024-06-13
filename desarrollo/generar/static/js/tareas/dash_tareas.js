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
      button.addEventListener("dragstart", () => {
        button.classList.add("dragging"); // Add visual indicator
      });
      button.addEventListener("dragend", () => {
        button.classList.remove("dragging"); // Remove visual indicator
      });
    });
    function updateTaskStatus(taskId, newStatus) {
        fetch('Estados/', { // Reemplaza '/update-task-status/' con la URL de tu endpoint
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ taskId, newStatus }),
        })
       .then(response => response.json())
       .then(data => {
          if (data.success) {
            console.log('Estado de la tarea actualizado exitosamente');
          } else {
            console.error('Error al actualizar el estado de la tarea');
          }
        })
       .catch((error) => {
          console.error('Error:', error);
        });
      }

    const completasList = document.querySelector("#second-block ul");

    completasList.addEventListener("dragover", event => {
        event.preventDefault(); // Allow dropping
    });

    completasList.addEventListener("drop", event => {
        const button = event.dataTransfer.getData("text/plain"); // Get dragged button ID
        const draggedButton = document.getElementById(button);
        
        updateTaskStatus(draggedButton.dataset.id, 'completa');
        // Update task status to "completa" here (using AJAX or form submission)
        completasList.appendChild(draggedButton); // Move button to "completas" list
        // Update task visually (optional):
        draggedButton.classList.remove("btn-primary").addClass("btn-success"); // Change button color
    });
});
