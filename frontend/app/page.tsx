// app/mainpage/page.tsx
import Link from 'next/link';

const MainPage = () => {
  return (
    <div style={{ width: "100%", maxWidth: "600px", margin: "0 auto", padding: "20px", backgroundColor: "#f0f0f0", border: "1px solid #ccc", borderRadius: "5px", fontFamily: "Tahoma, sans-serif" }}>
      <h1 style={{ textAlign: "center", color: "#0033cc" }}>RNA Sequence Analysis</h1>
      <div style={{ textAlign: "center", marginBottom: "20px" }}>
        <Link href="/pair">
          <button style={{ width: "100%", padding: "10px", backgroundColor: "#0078d4", color: "white", border: "none", borderRadius: "3px", cursor: "pointer", fontSize: "16px", marginBottom: "10px" }}>Scenario 1</button>
        </Link>
        <Link href="/single">
          <button style={{ width: "100%", padding: "10px", backgroundColor: "#0078d4", color: "white", border: "none", borderRadius: "3px", cursor: "pointer", fontSize: "16px", marginBottom: "10px" }}>Scenario 2</button>
        </Link>
        <Link href="/about">
          <button style={{ width: "100%", padding: "10px", backgroundColor: "#0078d4", color: "white", border: "none", borderRadius: "3px", cursor: "pointer", fontSize: "16px" }}>About</button>
        </Link>
      </div>
    </div>
  );
};

export default MainPage;
