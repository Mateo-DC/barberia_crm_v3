'use strict';
const service = document.getElementById('sale-service');
const amount = document.getElementById('sale-amount');
service.addEventListener('change', () => {
  const suggested = service.selectedOptions[0]?.dataset.price;
  if (suggested !== undefined) amount.value = Number(suggested).toFixed(2);
});
