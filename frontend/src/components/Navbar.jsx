
import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          Pastebin<span>Lite</span>
        </Link>

        <div className="navbar-links">
          <Link to="/">Create Paste</Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
