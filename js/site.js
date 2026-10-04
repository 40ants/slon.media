(function () {
  'use strict';

  const menu = document.querySelector('.mobile-menu');
  if (!menu) return;

  const toggle = menu.querySelector('summary');
  const desktop = window.matchMedia('(min-width: 701px)');

  document.addEventListener('pointerdown', function (event) {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && menu.open) {
      menu.open = false;
      toggle.focus();
    }
  });

  document.addEventListener('focusin', function (event) {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  });

  menu.querySelector('nav').addEventListener('click', function (event) {
    if (event.target.closest('a')) menu.open = false;
  });

  desktop.addEventListener('change', function (event) {
    if (event.matches) menu.open = false;
  });
}());
