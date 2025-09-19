// MENU LATERAL
const menuBtn = document.querySelector('.menu-btn');
const sidebar = document.querySelector('.sidebar');

menuBtn.addEventListener('click', () => {
    sidebar.classList.toggle('active');
});

const faqs = document.querySelectorAll('.painel .faq');

faqs.forEach(faq => {
  faq.addEventListener('click', () => {
    faqs.forEach(f => {
      if (f !== faq) f.classList.remove('active');
    });
    faq.classList.toggle('active');
  });
});


