import { useEffect, useState } from 'react';
import keycloak, { initKeycloak } from './keycloak';
import Dashboard from './pages/Dashboard';
import LoginPage from './pages/LoginPage';

function App() {
  const [keycloakInitialized, setKeycloakInitialized] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    initKeycloak()
      .then(auth => {
        console.log("Authenticated?", auth);
        setAuthenticated(auth);
        if (auth) {
          localStorage.setItem('token', keycloak.token);

          setInterval(() => {
            keycloak.updateToken(60)
              .then((refreshed) => {
                if (refreshed) {
                  console.log('Token refreshed ✔️');
                  localStorage.setItem('token', keycloak.token);
                } else {
                  console.log('Token still valid 🙂');
                }
              })
              .catch(() => {
                console.error('Token refresh failed ❌ - logging out');
                keycloak.logout({ redirectUri: window.location.origin });
              });
          }, 30000); // la fiecare 30 secunde verificăm
        }
        setKeycloakInitialized(true);
      })
      .catch(error => {
        console.error("Keycloak init error", error);
        setKeycloakInitialized(true);
      });
  }, []);

  if (!keycloakInitialized) {
    return <div>Loading Keycloak...</div>;
  }

  if (!authenticated) {
    return <LoginPage />;
  }  

  return (
    <Dashboard />
  );
}

export default App;
