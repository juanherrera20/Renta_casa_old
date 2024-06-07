function resetForm() {
    const forms = document.querySelectorAll("#addTarea, #addPropietario, #addInquilino, #addInmueble");
    forms.forEach(form => form.reset());
}
