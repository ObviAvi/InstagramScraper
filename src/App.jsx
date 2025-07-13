import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [displayMode, setDisplayMode] = useState("all");
  const [fadeOut, setFadeOut] = useState(false);
  const [showLists, setShowLists] = useState(false);

  useEffect(() => {
    if (!sessionStorage.getItem('warningShown')) {
      alert("After you enter your username and password, the scraper will automatically open an Instagram client and begin navigating. You don't need to take any action at this point—just wait for it to finish. If it encounters a security verification check, it will pause and wait for you to enter the verification code before continuing to scrape your followers and followings.");
      sessionStorage.setItem('warningShown', 'true');
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setFadeOut(true); // Start fade-out effect
    
    setTimeout(async () => {
      try {
        const response = await fetch('http://localhost:8000/scrape', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ username, password })
        });
        if (!response.ok) throw new Error("Scraping failed");
        const data = await response.json();
        setResult(data);
        setDisplayMode("all");
        setFadeOut(false); // Reset fade-out
        setShowLists(true); // Trigger list fade-in
      } catch (error) {
        setResult({ error: error.message });
        setFadeOut(false); // Reset fade-out even on error
      }
      setLoading(false);
    }, 500); // Matches CSS transition time
  };

  const handleReset = () => {
    setFadeOut(true); // Trigger fade-out

    setTimeout(() => {
      setUsername("");
      setPassword("");
      setResult(null);
      setShowLists(false);
      setFadeOut(false);
    }, 500);
  };

  const toggleDisplayMode = () => {
    setShowLists(false);
    setTimeout(() => {
      setDisplayMode(prevMode => (prevMode === "all" ? "nonMutual" : "all"));
      setShowLists(true);
    }, 300);
  };

  const renderLists = () => {
    if (!result) return null;
  
    return (
      <div className={`lists-container ${showLists ? 'show' : ''}`}>
        {displayMode === "all" ? (
          <>
            <div className="list-section">
              <h3>Followers ({result.followers.length})</h3>
              <ul>
                {result.followers.map((user, index) => (
                  <li key={index}>
                    <a href={`https://www.instagram.com/${user}`} target="_blank" rel="noopener noreferrer">
                      {user}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
            <div className="list-section">
              <h3>Following ({result.following.length})</h3>
              <ul>
                {result.following.map((user, index) => (
                  <li key={index}>
                    <a href={`https://www.instagram.com/${user}`} target="_blank" rel="noopener noreferrer">
                      {user}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </>
        ) : (
          <>
            <div className="list-section">
              <h3>Not Following You Back ({result.not_following_you_back.length})</h3>
              <ul>
                {result.not_following_you_back.map((user, index) => (
                  <li key={index}>
                    <a href={`https://www.instagram.com/${user}`} target="_blank" rel="noopener noreferrer">
                      {user}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
            <div className="list-section">
              <h3>Not Following Them Back ({result.not_following_them_back.length})</h3>
              <ul>
                {result.not_following_them_back.map((user, index) => (
                  <li key={index}>
                    <a href={`https://www.instagram.com/${user}`} target="_blank" rel="noopener noreferrer">
                      {user}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}
      </div>
    );
  };

  return (
    <div className="app-wrapper">
      <div className={`app-container ${result ? (fadeOut ? 'fade-out' : 'results-page') : (fadeOut ? 'fade-out' : '')}`}>
        <h1>Instagram Scraper</h1>
        
        {!result ? (
          <form onSubmit={handleSubmit} className="scraper-form">
            <div className="form-group">
              <label htmlFor="username">Instagram Username</label>
              <input
                id="username"
                type="text"
                placeholder="Enter your Instagram username"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Instagram Password</label>
              <input
                id="password"
                type="password"
                placeholder="Enter your Instagram password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" disabled={loading}>
              {loading ? "Scraping..." : "Submit"}
            </button>
          </form>
        ) : (
          <div className="results-content">
            {result.followers && result.following ? (
              <>
                {renderLists()}
                <button onClick={toggleDisplayMode} className="toggle-button">
                  {displayMode === "all" ? "Show Non-Mutual Lists" : "Show All Lists"}
                </button>
              </>
            ) : result.error ? (
              <p className="error">{result.error}</p>
            ) : (
              <pre>{JSON.stringify(result, null, 2)}</pre>
            )}
            <button onClick={handleReset} className="reset-button">
              Scrape New Account
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;