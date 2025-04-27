import Keycloak from "keycloak-js";

const keycloak = new Keycloak({
    url: "http://localhost:8080/auth",
    realm: "foodtracker",
    clientId: "foodtracker-frontend",
});

let keycloakInitPromise = null;

export const initKeycloak = () => {
    if (!keycloakInitPromise) {
        keycloakInitPromise = keycloak.init({
            onLoad: 'check-sso',
            silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
            pkceMethod: 'S256'
        });
    }
    return keycloakInitPromise;
};

export default keycloak;
