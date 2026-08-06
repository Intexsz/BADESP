function handleCredentialResponse(response) {
    const urlPost = document.body.getAttribute("data-url") || "/Login";

    fetch(urlPost, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ credential: response.credential })
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === "ok") {
                window.location.href = "/Inicio";
            } else {
                alert("Erro no login Google.");
            }
        })
        .catch(err => console.error("Erro na requisição:", err));
}


    window.onload = function () {
        google.accounts.id.initialize({
            client_id: "177205671715-238eoh4gfa3qusnfuuaa9jmctiot8vno.apps.googleusercontent.com",
            callback: handleCredentialResponse
        });

    google.accounts.id.renderButton(
    document.getElementById("googleSignInBtn"),
    {theme: "outline", size: "large" }
    );
};
