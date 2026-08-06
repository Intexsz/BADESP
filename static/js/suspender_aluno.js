document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('formSuspender');
    if (form) {
        form.addEventListener('submit', function (e) {
            const confirmacao = confirm('Tem certeza que deseja suspender este aluno?');
            if (!confirmacao) {
                e.preventDefault(); // Cancela o envio se clicar em "Cancelar"
            }
        });
    }
});