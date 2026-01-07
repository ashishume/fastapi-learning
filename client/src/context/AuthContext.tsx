import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
import { authApi } from "../api";

interface User {
  email: string;
  id?: string;
  name?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  setUser: (user: User | null) => void;
  login: (email: string, id: string, name: string) => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const response = await authApi.get("/user_details", {
          withCredentials: true,
        });
        setUser({
          email: response.data.email,
          id: response.data.id,
          name: response.data.name,
        });
      } catch (error) {
        // User is not authenticated
        setUser(null);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const login = (email: string, id: string, name: string) => {
    // Set user after successful login
    setUser({ email, id, name });
  };

  const logout = async () => {
    try {
      await authApi.post("/logout");
      setUser(null);
    } catch (error) {
      // Even if the logout request fails, clear the user state
      console.error("Logout request failed:", error);
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: user !== null && user !== undefined,
        loading,
        setUser,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
