
const btn = document.querySelector('.menu-btn');
const sidebar = document.querySelector('.sidebar');

btn.addEventListener('click', () => sidebar.classList.toggle('ativo'));

function confirmarLogout(e) {
    e.preventDefault();
    if (confirm("Deseja realmente sair?")) {
        window.location.href = "/Logout";
    }
}

document.addEventListener("click", (e) => {
    if (!sidebar.contains(e.target) && !btn.contains(e.target)) {
        sidebar.classList.remove("ativo");
    }
});

document.getElementById("feedback-form").addEventListener("submit", function (e) {
    const titulo = document.getElementById("titulo").value.trim();
    const feedback = document.getElementById("feedback").value.trim();

    if (titulo.length < 3) {
        alert("Título muito curto.");
        e.preventDefault();
    }

    if (feedback.length < 10) {
        alert("Feedback muito curto.");
        e.preventDefault();
    }
});