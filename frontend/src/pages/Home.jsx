const Home = () => {
  return (
    <div className="bg-dark text-white">
      {/* Hero Section */}
      <div className="bg-black py-5 text-center" style={{height: "90vh", display: "flex", alignItems: "center"}}>
        <div className="container">
          <h1 className="display-1 fw-bold mb-4">Cinema Stream</h1>
          <p className="lead fs-3 mb-5">Watch Movies & TV Shows Like Never Before</p>
          import { Link } from "react-router-dom";

<Link to="/browse" className="btn btn-danger btn-lg px-5 py-3 fs-5">
  Browse Now
</Link>

        </div>
      </div>

      <div className="container py-5">
        <h2 className="text-center mb-5">Trending This Week</h2>
        <div className="alert alert-success text-center">
          ✅ React Frontend متصل بنجاح مع Django Backend
        </div>
      </div>
    </div>
  )
}

export default Home