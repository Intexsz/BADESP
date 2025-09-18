function googleSignIn() {
    gapi.auth2.getAuthInstance().signIn().then(function(googleUser) {
        var profile = googleUser.getBasicProfile();
        console.log("ID: " + profile.getId());
        console.log("Nome: " + profile.getName());
        console.log("Email: " + profile.getEmail());
        // Aqui você pode enviar as informações para o seu servidor ou fazer o que precisar
    });
}

// Função para inicializar o Google Sign-In
function initGoogleSignIn() {
    gapi.load('auth2', function() {
        gapi.auth2.init({
            client_id: 'SUA_CLIENT_ID_AQUI.apps.googleusercontent.com'
        });
    });
}

// Inicializa o Google Sign-In ao carregar a página
window.onload = initGoogleSignIn;