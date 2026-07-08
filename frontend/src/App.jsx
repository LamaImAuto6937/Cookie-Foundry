import { useState, useEffect } from 'react';

function App() {
  const [cookies, setCookies] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/cookies')
      .then((response) => response.json())
      .then((data) => setCookies(data.cookies));
  }, []);

  return (
    <div>
      <h1>Cookie Foundry</h1>
      <p>Aktuelle Kekse: {cookies}</p>
    </div>
  );
}

export default App;