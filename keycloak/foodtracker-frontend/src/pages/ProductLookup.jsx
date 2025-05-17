import { useState } from 'react';

function ProductLookup(props) {
  const [barcode, setBarcode] = useState('');
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaved(false);
    setError('');
    setProduct(null);
    if (!barcode) return;

    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5010/api/product?barcode=${barcode}`);
      if (!response.ok) throw new Error("Produsul nu a fost găsit");

      const data = await response.json();
      setProduct(data);
    } catch (err) {
      setError(err.message || "Eroare necunoscută");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!product) return;
    const token = localStorage.getItem("token");

    try {
      const res = await fetch("http://localhost:5000/products", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          barcode: barcode,
          name: product.name,
          quantity: product.quantity,
          calories: product.nutriments.calories,
          image: product.image
        })
      });

      if (res.ok) {
        setSaved(true);
        setBarcode('');
        setProduct(null);
        props.onProductSaved?.(); // 👈 Trigger reîncărcare Dashboard
      } else {
        const errData = await res.json();
        setError(errData.error || "Eroare la salvare");
      }
    } catch (err) {
      setError("Eroare rețea la salvare");
    }
  };

  return (
    <div style={{ marginBottom: "10px", color: "#2c3e50" }}>
      <h3>🔎 Adaugă produs în inventar</h3>
      <form onSubmit={handleSubmit} style={{ marginBottom: '10px' }}>
        <input
        className="barcode-input"
        type="text"
        value={barcode}
        onChange={(e) => setBarcode(e.target.value)}
        placeholder="Introdu codul de bare (ex: 5449000000996)"
        style={{
            padding: '10px',
            width: '300px',
            fontSize: '16px',
            backgroundColor: '#000',
            color: '#fff',
            border: '1px solid #ccc',
            borderRadius: '5px'
        }}
        />

        <button type="submit" style={{ marginLeft: '10px', padding: '10px 20px' }}>
          Caută
        </button>
      </form>

      {loading && <p>Se caută produsul...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {saved && <p style={{ color: 'green' }}>✅ Produs salvat!</p>}

      {product && (
        <div style={{
          border: '1px solid #ccc',
          borderRadius: '10px',
          padding: '20px',
          maxWidth: '500px',
          marginTop: '20px',
          backgroundColor: '#f9f9f9'
        }}>
          <h4>{product.name}</h4>
          <p><strong>Cantitate:</strong> {product.quantity}</p>
          <p><strong>Calorii:</strong> {product.nutriments.calories}</p>
          {product.image && (
            <img src={product.image} alt={product.name} style={{ width: '200px', marginTop: '10px' }} />
          )}
          <br />
          <button
            onClick={handleSave}
            style={{
              marginTop: '10px',
              padding: '10px 20px',
              backgroundColor: '#2ecc71',
              color: 'white',
              border: 'none',
              borderRadius: '5px'
            }}
          >
            Salvează produsul
          </button>
        </div>
      )}
    </div>
  );
}

export default ProductLookup;
