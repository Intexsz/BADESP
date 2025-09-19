const form = document.getElementById("form-denuncia");
const container = document.getElementById("denuncias-container");

form.addEventListener("submit", function(e){
  e.preventDefault();
  const titulo = document.getElementById("titulo").value;
  const gravidade = document.getElementById("gravidade").value;
  const resposta = document.getElementById("resposta").value;

  const card = document.createElement("div");
  card.classList.add("denuncia-card");
  card.innerHTML = `
    <h3>${titulo}</h3>
    <p>Ocorrido: ${gravidade}</p>
    <p>Denúncia: ${resposta || "Aguardando..."}</p>
    <p>Data: ${new Date().toLocaleDateString()}</p>
  `;
  container.prepend(card);
  form.reset();
});

const btn = document.querySelector('.menu-btn');
const sidebar = document.querySelector('.sidebar');

btn.addEventListener('click', () => {
  sidebar.classList.toggle('active');
});
