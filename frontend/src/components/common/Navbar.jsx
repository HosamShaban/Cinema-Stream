import { Link } from "react-router-dom"

function Navbar() {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark px-3">
      <Link className="navbar-brand" to="/">Cinema Stream</Link>
      <ul className="navbar-nav ms-auto">
        <li className="nav-item"><Link className="nav-link" to="/">Home</Link></li>
        <li className="nav-item"><Link className="nav-link" to="/browse">Browse</Link></li>
        <li className="nav-item"><Link className="nav-link" to="/profile">Profile</Link></li>
        <li className="nav-item"><Link className="nav-link" to="/login">Login</Link></li>
      </ul>
    </nav>
  )
}

export default Navbar
