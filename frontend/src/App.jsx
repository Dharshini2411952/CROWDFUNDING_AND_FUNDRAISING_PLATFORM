import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [page, setPage] = useState("login");
  const [user, setUser] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [loginData, setLoginData] = useState({
    email: "",
    password: "",
  });

  const [signupData, setSignupData] = useState({
    name: "",
    email: "",
    password: "",
    phone: "",
    role: "USER",
  });

  // =========================
  // LOGIN
  // =========================

  const handleLogin = async (e) => {
    e.preventDefault();

    setMessage("");
    setLoading(true);

    try {
      const response = await axios.post(
        `${API_URL}/auth/login`,
        loginData,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      console.log("LOGIN RESPONSE:", response.data);

      const token = response.data.access_token;

      if (!token) {
        throw new Error("Access token not received");
      }

      localStorage.setItem("token", token);

      setUser({
        email: loginData.email,
      });

      setMessage("");
      setPage("dashboard");
    } catch (error) {
      console.error("LOGIN ERROR:", error);

      if (error.response) {
        setMessage(
          error.response.data?.detail ||
            "Invalid email or password."
        );
      } else if (error.request) {
        setMessage(
          "Cannot connect to backend. Make sure FastAPI is running."
        );
      } else {
        setMessage("Login failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // SIGNUP
  // =========================

  const handleSignup = async (e) => {
    e.preventDefault();

    setMessage("");
    setLoading(true);

    try {
      const response = await axios.post(
        `${API_URL}/auth/signup`,
        signupData,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      console.log("SIGNUP RESPONSE:", response.data);

      setLoginData({
        email: signupData.email,
        password: signupData.password,
      });

      setMessage(
        "Account created successfully! Please login."
      );

      setTimeout(() => {
        setPage("login");
        setMessage("");
      }, 1500);
    } catch (error) {
      console.error("SIGNUP ERROR:", error);

      if (error.response) {
        setMessage(
          error.response.data?.detail ||
            "Signup failed. Please try again."
        );
      } else if (error.request) {
        setMessage(
          "Cannot connect to backend. Make sure FastAPI is running."
        );
      } else {
        setMessage("Signup failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // LOGOUT
  // =========================

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUser(null);
    setPage("login");
    setMessage("");
  };

  // =========================
  // LOGIN PAGE
  // =========================

  if (page === "login") {
    return (
      <div className="auth-page">

        <div className="brand-section">
          <div className="brand-logo">F</div>

          <h1>Fund AI</h1>

          <p>
            Empowering ideas.
            <br />
            Supporting dreams.
          </p>

          <div className="brand-features">
            <div>✓ Support meaningful campaigns</div>
            <div>✓ Discover inspiring ideas</div>
            <div>✓ Make an impact</div>
          </div>
        </div>

        <div className="auth-card">

          <div className="card-header">
            <h2>Welcome back 👋</h2>
            <p>Login to your Fund AI account</p>
          </div>

          <form onSubmit={handleLogin}>

            <div className="input-group">
              <label>Email Address</label>

              <input
                type="email"
                placeholder="Enter your email"
                value={loginData.email}
                onChange={(e) =>
                  setLoginData({
                    ...loginData,
                    email: e.target.value,
                  })
                }
                required
              />
            </div>

            <div className="input-group">
              <label>Password</label>

              <input
                type="password"
                placeholder="Enter your password"
                value={loginData.password}
                onChange={(e) =>
                  setLoginData({
                    ...loginData,
                    password: e.target.value,
                  })
                }
                required
              />
            </div>

            {message && (
              <div className="message">
                {message}
              </div>
            )}

            <button
              className="primary-btn"
              type="submit"
              disabled={loading}
            >
              {loading ? "Logging in..." : "Login"}
            </button>

          </form>

          <div className="switch-auth">
            <span>Don't have an account?</span>

            <button
              type="button"
              onClick={() => {
                setPage("signup");
                setMessage("");
              }}
            >
              Sign Up
            </button>
          </div>

        </div>
      </div>
    );
  }

  // =========================
  // SIGNUP PAGE
  // =========================

  if (page === "signup") {
    return (
      <div className="auth-page">

        <div className="brand-section">
          <div className="brand-logo">F</div>

          <h1>Fund AI</h1>

          <p>
            Start supporting
            <br />
            meaningful ideas.
          </p>

          <div className="brand-features">
            <div>✓ Create campaigns</div>
            <div>✓ Support great ideas</div>
            <div>✓ Build a better future</div>
          </div>
        </div>

        <div className="auth-card signup-card">

          <div className="card-header">
            <h2>Create Account 🚀</h2>
            <p>Join the Fund AI community</p>
          </div>

          <form onSubmit={handleSignup}>

            <div className="input-group">
              <label>Full Name</label>

              <input
                type="text"
                placeholder="Enter your name"
                value={signupData.name}
                onChange={(e) =>
                  setSignupData({
                    ...signupData,
                    name: e.target.value,
                  })
                }
                required
              />
            </div>

            <div className="input-group">
              <label>Email Address</label>

              <input
                type="email"
                placeholder="Enter your email"
                value={signupData.email}
                onChange={(e) =>
                  setSignupData({
                    ...signupData,
                    email: e.target.value,
                  })
                }
                required
              />
            </div>

            <div className="input-group">
              <label>Phone Number</label>

              <input
                type="tel"
                placeholder="Enter phone number"
                value={signupData.phone}
                onChange={(e) =>
                  setSignupData({
                    ...signupData,
                    phone: e.target.value,
                  })
                }
              />
            </div>

            <div className="input-group">
              <label>Password</label>

              <input
                type="password"
                placeholder="Create password"
                value={signupData.password}
                onChange={(e) =>
                  setSignupData({
                    ...signupData,
                    password: e.target.value,
                  })
                }
                required
              />
            </div>

            {message && (
              <div className="message success-message">
                {message}
              </div>
            )}

            <button
              className="primary-btn"
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Creating account..."
                : "Create Account"}
            </button>

          </form>

          <div className="switch-auth">
            <span>Already have an account?</span>

            <button
              type="button"
              onClick={() => {
                setPage("login");
                setMessage("");
              }}
            >
              Login
            </button>
          </div>

        </div>
      </div>
    );
  }

  // =========================
  // DASHBOARD
  // =========================

  return (
    <div className="dashboard">

      <nav className="navbar">

        <div className="nav-logo">
          <div className="small-logo">F</div>
          <span>Fund AI</span>
        </div>

        <div className="nav-right">
          <span className="user-email">
            {user?.email}
          </span>

          <button
            className="logout-btn"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>

      </nav>

      <main className="dashboard-content">

        <section className="welcome">

          <div>
            <p className="small-title">
              FUND AI DASHBOARD
            </p>

            <h1>
              Welcome back 👋
            </h1>

            <p>
              Discover campaigns and support ideas
              that make a difference.
            </p>
          </div>

          <button className="create-btn">
            + Create Campaign
          </button>

        </section>

        <section className="stats">

          <div className="stat-card">
            <div className="stat-icon">📢</div>
            <div>
              <span>Active Campaigns</span>
              <h2>12</h2>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">💰</div>
            <div>
              <span>Total Donations</span>
              <h2>₹25,000</h2>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">❤️</div>
            <div>
              <span>My Donations</span>
              <h2>₹5,000</h2>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🎯</div>
            <div>
              <span>My Campaigns</span>
              <h2>3</h2>
            </div>
          </div>

        </section>

        <section className="campaign-section">

          <div className="section-heading">

            <div>
              <h2>Featured Campaigns</h2>
              <p>
                Support campaigns that matter
              </p>
            </div>

            <button className="view-btn">
              View All →
            </button>

          </div>

          <div className="campaign-grid">

            <div className="campaign-card">

              <div className="campaign-image">
                🌱
              </div>

              <div className="campaign-body">

                <span className="category">
                  Environment
                </span>

                <h3>
                  Green Future Project
                </h3>

                <p>
                  Help us create a greener and
                  healthier environment.
                </p>

                <div className="progress">
                  <div
                    className="progress-fill"
                    style={{ width: "75%" }}
                  ></div>
                </div>

                <div className="campaign-amount">
                  <strong>₹75,000</strong>
                  <span>of ₹1,00,000</span>
                </div>

                <button className="support-btn">
                  Support Campaign
                </button>

              </div>

            </div>

            <div className="campaign-card">

              <div className="campaign-image purple">
                🎓
              </div>

              <div className="campaign-body">

                <span className="category">
                  Education
                </span>

                <h3>
                  Education For All
                </h3>

                <p>
                  Support education opportunities
                  for deserving students.
                </p>

                <div className="progress">
                  <div
                    className="progress-fill"
                    style={{ width: "67%" }}
                  ></div>
                </div>

                <div className="campaign-amount">
                  <strong>₹40,000</strong>
                  <span>of ₹60,000</span>
                </div>

                <button className="support-btn">
                  Support Campaign
                </button>

              </div>

            </div>

          </div>

        </section>

      </main>

    </div>
  );
}

export default App;