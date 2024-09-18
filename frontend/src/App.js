import React from 'react';
import './App.css';


function App() {
  const handleClick = () => {
    alert('Button clicked!');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>snp-app</h1>
        <button onClick={handleClick}>Run</button>
      </header>
    </div>
  );
}

export default App;
