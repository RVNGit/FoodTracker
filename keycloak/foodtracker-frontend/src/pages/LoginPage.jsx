import keycloak from "../keycloak";

function LoginPage() {
  const handleLogin = () => {
    keycloak.login();
  };

  return (
    <div style={{
      height: "100vh",
      width: "100vw",
      background: "linear-gradient(to bottom right, #3498db, #2ecc71)",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      flexDirection: "column",
      color: "white"
    }}>
      <h1 style={{
        fontSize: "48px",
        marginBottom: "20px",
        display: "flex",
        alignItems: "center",
        gap: "10px"
      }}>
        FoodTracker
        <span style={{ fontSize: "48px" }}>🥑</span>
      </h1>

      <button
        onClick={handleLogin}
        style={{
          padding: "15px 30px",
          fontSize: "20px",
          fontWeight: "bold",
          borderRadius: "8px",
          border: "none",
          cursor: "pointer",
          backgroundColor: "#2c3e50",
          color: "white",
          transition: "background 0.3s"
        }}
        onMouseOver={(e) => e.target.style.backgroundColor = "#34495e"}
        onMouseOut={(e) => e.target.style.backgroundColor = "#2c3e50"}
      >
        Login
      </button>
    </div>
  );
}

export default LoginPage;
