window.onload = function() {
    document.getElementById('buscar').addEventListener('input', function() {
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