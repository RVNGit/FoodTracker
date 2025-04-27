import keycloak from "../keycloak";

function Dashboard() {
  const handleLogout = () => {
    keycloak.logout({
      redirectUri: window.location.origin
    });
    localStorage.removeItem('token');
  };

  return (
    <div style={{
      height: "100vh",
      width: "100vw",
      backgroundColor: "#f0f2f5",
      display: "flex",
      flexDirection: "column"
    }}>
      {/* Header bar */}
      <div style={{
        width: "100%",
        minHeight: "70px",
        backgroundColor: "#ffffff",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        boxShadow: "0 2px 4px rgba(0,0,0,0.1)", 
      }}>
        <h2 style={{ marginLeft: "30px", color: "#2c3e50", fontSize: "28px" }}>
          🥑 FoodTracker Dashboard
        </h2>
        <button
          onClick={handleLogout}
          style={{
            marginRight: "30px",
            fontSize: "16px",
            backgroundColor: "#e74c3c",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            fontWeight: "bold",
            transition: "background 0.3s",
            whiteSpace: "nowrap"
          }}
          onMouseOver={(e) => e.target.style.backgroundColor = "#c0392b"}
          onMouseOut={(e) => e.target.style.backgroundColor = "#e74c3c"}
        >
          Logout
        </button>
      </div>

      {/* Main content */}
      <div style={{
        width: "100%",
        flex: 1,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        fontSize: "24px",
        color: "#2c3e50"
      }}>
        Bine ai venit! 🎉
      </div>
    </div>
  );
}

export default Dashboard;
