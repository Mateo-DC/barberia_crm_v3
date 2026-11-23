'use strict';
const form = document.getElementById('service-form');
const reset = document.getElementById('service-reset');
for (const button of document.querySelectorAll('[data-edit-service]')) {
  button.addEventListener('click', () => {
    document.getElementById('service-id').value = button.dataset.id;
    document.getElementById('service-name').value = button.dataset.name;
    document.getElementById('service-price').value = button.dataset.price;
    document.getElementById('service-heading').textContent = 'Editar servicio';
    document.getElementById('service-name').focus();
  });
}
reset.addEventListener('click', () => {
  form.reset(); document.getElementById('service-id').value = '0';
  document.getElementById('service-heading').textContent = 'Nuevo servicio';
});
