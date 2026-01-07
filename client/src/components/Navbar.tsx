import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getWorkspaces } from "../api/document";
import { useQuery } from "@tanstack/react-query";

function Navbar() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const onLogoutHandler = async () => {
    try {
      await logout();
      navigate("/login", { replace: true });
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const { data: workspaces } = useQuery({
    queryKey: ["workspaces"],
    queryFn: () => getWorkspaces(),
  });

  console.log(workspaces);
  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="text-xl font-bold hover:text-blue-200">
            FastAPI Learning
          </Link>
          <div className="flex space-x-6">
            {/* <Link
              to="/movies"
              className="hover:text-blue-200 transition-colors"
            >
              Movies
            </Link> */}
            {/* <Link to="/about" className="hover:text-blue-200 transition-colors">
              About
            </Link> */}
            <select>
              <option value="movies">Movies</option>
              <option value="about">About</option>
            </select>
            <button onClick={onLogoutHandler}>Logout</button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
