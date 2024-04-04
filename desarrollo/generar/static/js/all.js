function resetForm() {
    const forms = document.querySelectorAll("#addTarea, #addPropietario, #addInquilino");
    forms.forEach(form => form.reset());
}
