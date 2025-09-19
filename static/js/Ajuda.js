// MENU LATERAL
const menuBtn = document.querySelector('.menu-btn');
const sidebar = document.querySelector('.sidebar');

menuBtn.addEventListener('click', () => {
    sidebar.classList.toggle('active');
});

// ACORDEÃO FAQ
const faqs = document.querySelectorAll('#ajuda .faq');

faqs.forEach(faq => {
    const pergunta = faq.querySelector('h3');

    pergunta.addEventListener('click', () => {
        // Fecha outras FAQs abertas
        faqs.forEach(f => {
            if (f !== faq) {
                f.classList.remove('active');
            }
        });

        // Alterna a FAQ clicada
        faq.classList.toggle('active');
    });
});
