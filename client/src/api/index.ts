import axios from "axios";
const AUTH_BASE_URL = import.meta.env.VITE_AUTH_API_URL;
const BOOKING_BASE_URL = import.meta.env.VITE_BOOKING_API_URL;

export const authApi = axios.create({
  baseURL: AUTH_BASE_URL,
  withCredentials: true, // Enable sending cookies with requests
});

export const bookingApi = axios.create({
  baseURL: BOOKING_BASE_URL,
  withCredentials: true, // Enable sending cookies with requests
});

// Add response interceptor to handle authentication errors globally
const setupInterceptor = (logoutCallback: () => void) => {
  const interceptor = (error: any) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear user state
      logoutCallback();
    }
    return Promise.reject(error);
  };

  authApi.interceptors.response.use((response) => response, interceptor);
  bookingApi.interceptors.response.use((response) => response, interceptor);
};

export { setupInterceptor };

export const login = async (email: string, password: string) => {
  const response = await authApi.post("/auth/login", { email, password });
  return response.data;
};

export const signup = async (email: string, password: string) => {
  const response = await authApi.post("/auth/signup", { email, password });
  return response.data;
};

export const getMovies = async () => {
  const response = await bookingApi.get("/bookings");
  return response.data;
};

export const getBookingById = async (id: string) => {
  const response = await bookingApi.get(`/bookings/${id}`);
  return response.data;
};

export const createBooking = async (booking: any) => {
  const response = await bookingApi.post("/bookings", booking);
  return response.data;
};
