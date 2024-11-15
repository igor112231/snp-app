// app/about/page.tsx
const About = () => {
  const repeatedText = new Array(100).fill("text").join(" ");

  return (
    <div style={{ width: "100%", maxWidth: "600px", margin: "0 auto", padding: "20px", backgroundColor: "#f0f0f0", border: "1px solid #ccc", borderRadius: "5px", fontFamily: "Tahoma, sans-serif" }}>
      <h1 style={{ textAlign: "center", color: "#0033cc" }}>About</h1>
      <p style={{ fontSize: "14px", color: "#555", textAlign: "center" }}>{repeatedText}</p>
    </div>
  );
};

export default About;
