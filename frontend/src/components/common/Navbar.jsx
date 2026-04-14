import { Link } from 'react-router-dom'

const Navbar = () => {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
      <div className="container-fluid">
        <Link className="navbar-brand fw-bold fs-3" to="/">🎬 Cinema Stream</Link>
        <div className="navbar-nav ms-auto">
          <Link className="nav-link mx-2" to="/">Home</Link>
          <Link className="nav-link mx-2" to="/browse">Browse</Link>
          <Link className="nav-link mx-2" to="/profile">Profile</Link>
          <Link className="nav-link mx-2 btn btn-outline-light" to="/login">Login</Link>
        </div>
      </div>
    </nav>
  )
}

export default Navbar