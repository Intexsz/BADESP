document.addEventListener("DOMContentLoaded", function () {
    const btnCopiar = document.getElementById("btnCopiar");
    const secretKeySpan = document.getElementById("secretKey");

    if (btnCopiar && secretKeySpan) {
        btnCopiar.addEventListener("click", function () {
            const textoParaCopiar = secretKeySpan.textContent.trim();

            navigator.clipboard.writeText(textoParaCopiar).then(function () {
                alert("Chave copiada com sucesso!");
            }).catch(function (err) {
                console.error("Erro ao tentar copiar a chave: ", err);
            });
        });
    }
});