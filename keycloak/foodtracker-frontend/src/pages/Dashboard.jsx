import { useEffect, useState } from "react";
import keycloak from "../keycloak";
import ProductLookup from "./ProductLookup";

function Dashboard() {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("name");
  const [order, setOrder] = useState("asc");
  const [page, setPage] = useState(1);
  const limit = 4;


  const handleLogout = () => {
    keycloak.logout({ redirectUri: window.location.origin });
    localStorage.removeItem("token");
  };

  const refreshProducts = () => {
    const token = localStorage.getItem("token");
    if (!token) return;

    const params = new URLSearchParams({
      search,
      sort,
      order,
      page,
      limit
    });

    fetch(`http://localhost:5000/products?${params.toString()}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => {
        if (!data.error) {
          setProducts(data);
        } else {
          console.error("Eroare la fetch produse:", data.error);
        }
      })
      .catch(err => {
        console.error("Eroare rețea:", err);
      });
  };


  const handleDelete = async (productId) => {
  const token = localStorage.getItem("token");
  try {
      const res = await fetch(`http://localhost:5000/products/${productId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (res.ok) {
        refreshProducts(); // Reîncarcă lista
      } else {
        const errData = await res.json();
        alert("Eroare la ștergere: " + errData.error);
      }
    } catch (err) {
      alert("Eroare rețea la ștergere");
    }
  };

  useEffect(() => {
    refreshProducts();
  }, [search, sort, order, page]);

  return (
  <div style={{
    height: "100vh",
    width: "100vw",
    backgroundColor: "#f0f2f5",
    display: "flex",
    flexDirection: "column"
  }}>
    {/* Header */}
    <div style={{
      width: "100%",
      minHeight: "70px",
      backgroundColor: "#ffffff",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
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
          fontWeight: "bold"
        }}
      >
        Logout
      </button>
    </div>

    {/* Conținut principal */}
    <div style={{
      flex: 1,
      overflowY: "auto",
      padding: "40px 60px",
      display: "flex",
      flexDirection: "column",
      gap: "30px"
    }}>
      {/* Formular adăugare */}
      <ProductLookup onProductSaved={refreshProducts} />

      {/* 🔍 Căutare și sortare */}
      <div style={{ display: "flex", gap: "20px", alignItems: "center", marginBottom: "10px" }}>
        <input
          type="text"
          placeholder="Caută după nume..."
          value={search}
          onChange={(e) => {
            setPage(1);
            setSearch(e.target.value);
          }}
          style={{
            padding: "10px",
            border: "1px solid #ccc",
            borderRadius: "5px",
            fontSize: "16px",
            width: "250px"
          }}
        />
        <select value={sort} onChange={(e) => setSort(e.target.value)} style={{ padding: "10px" }}>
          <option value="name">Sortare: Nume</option>
          <option value="calories">Sortare: Calorii</option>
        </select>
        <select value={order} onChange={(e) => setOrder(e.target.value)} style={{ padding: "10px" }}>
          <option value="asc">Crescător</option>
          <option value="desc">Descrescător</option>
        </select>
      </div>

      {/* 🧾 Produse salvate */}
      <h3 style={{ color: "#2c3e50" }}>📦 Produsele tale:</h3>

      {products.length === 0 ? (
        <div style={{
          flex: 1,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          fontSize: "24px",
          color: "#2c3e50"
        }}>
          Niciun produs găsit.
        </div>
      ) : (
        <div style={{ display: "flex", flexWrap: "wrap", gap: "20px" }}>
          {products.map((prod) => (
            <div key={prod._id} style={{
              border: "1px solid #ccc",
              borderRadius: "10px",
              padding: "15px",
              width: "250px",
              backgroundColor: "#fff",
              display: "flex",
              flexDirection: "column",
              alignItems: "center"
            }}>
              <h4 style={{ color: "black", marginBottom: "5px", textAlign: "center"}}>{prod.name}</h4>
              <p style={{color: "black"}}><strong>Cod:</strong> {prod.barcode}</p>
              <p style={{color: "black"}}><strong>Calorii:</strong> {prod.calories} kcal</p>
              {
              prod.image && (
                <img src={prod.image} alt={prod.name} style={{
                  width: "180px",
                  height: "auto",
                  borderRadius: "6px",
                  marginBottom: "10px"
                }} />
              )}
              <button
                onClick={() => {
                  if (confirm("Ești sigur că vrei să ștergi acest produs?")) {
                    handleDelete(prod._id);
                  }
                }}
                style={{
                  padding: "8px 16px",
                  backgroundColor: "#e74c3c",
                  color: "white",
                  border: "none",
                  borderRadius: "5px",
                  cursor: "pointer",
                  fontWeight: "bold"
                }}
              >
                🗑️ Șterge
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Paginare */}
      <div style={{ marginTop: "20px", display: "flex", gap: "20px" }}>
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          ◀️ Pagina anterioară
        </button>

        <span style={{ color: '#000', fontWeight: 'bold' }}>Pagina {page}</span>

        <button
          onClick={() => setPage((p) => p + 1)}
          disabled={products.length < limit}
        >
          Pagina următoare ▶️
        </button>
      </div>
    </div>
  </div>
);

}

export default Dashboard;
