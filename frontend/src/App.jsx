import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [page, setPage] = useState("login");

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

  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");

  const [user, setUser] = useState(null);

  // =========================
  // LOGIN
  // =========================

  const handleLogin = async (e) => {
    e.preventDefault();

    setMessage("");
    setMessageType("");

    try {
      const response = await axios.post(
        `${API_URL}/auth/login`,
        loginData
      );

      console.log("LOGIN RESPONSE:", response.data);

      const token = response.data.access_token;

      if (!token) {
        setMessage("Login failed. Access token not received.");
        setMessageType("error");
        return;
      }

      // Save token
      localStorage.setItem("token", token);

      // Get role from backend response
      const role = response.data.role;

      setUser({
        email: loginData.email,
        role: role || "USER",
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
      } else {
        setMessage(
          "Cannot connect to backend. Make sure FastAPI is running."
        );
      }

      setMessageType("error");
    }
  };

  // =========================
  // SIGNUP
  // =========================

  const handleSignup = async (e) => {
    e.preventDefault();

    setMessage("");
    setMessageType("");

    try {
      console.log("SIGNUP DATA:", signupData);

      await axios.post(
        `${API_URL}/auth/signup`,
        signupData
      );

      setMessage(
        "Account created successfully! Please login."
      );

      setMessageType("success");

      // Automatically fill login details
      setLoginData({
        email: signupData.email,
        password: signupData.password,
      });

      // Go to login
      setTimeout(() => {
        setPage("login");
        setMessage("");
        setMessageType("");
      }, 1500);

    } catch (error) {
      console.error("SIGNUP ERROR:", error);

      if (error.response) {
        setMessage(
          error.response.data?.detail ||
          "Signup failed. Please try again."
        );
      } else {
        setMessage(
          "Cannot connect to backend. Make sure FastAPI is running."
        );
      }

      setMessageType("error");
    }
  };

  // =========================
  // LOGOUT
  // =========================

  const handleLogout = () => {
    localStorage.removeItem("token");

    setUser(null);

    setLoginData({
      email: "",
      password: "",
    });

    setPage("login");
  };

  // =========================
  // LOGIN PAGE
  // =========================

  if (page === "login") {
    return (
      <div className="page">

        <div className="auth-box">

          {/* BRAND */}
          <div className="brand">

            <div className="logo">
              F
            </div>

            <h1>Fund AI</h1>

            <p>
              Empowering ideas. Supporting dreams.
            </p>

          </div>

          {/* FORM */}
          <div className="form-section">

            <h2>Welcome Back</h2>

            <p className="subtitle">
              Login to your Fund AI account
            </p>

            <form onSubmit={handleLogin}>

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

              {message && (
                <div className={`message ${messageType}`}>
                  {message}
                </div>
              )}

              <button type="submit">
                Login
              </button>

            </form>

            <p className="switch">
              Don't have an account?

              <span
                onClick={() => {
                  setPage("signup");
                  setMessage("");
                  setMessageType("");
                }}
              >
                Sign Up
              </span>
            </p>

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
      <div className="page">

        <div className="auth-box">

          {/* BRAND */}
          <div className="brand">

            <div className="logo">
              F
            </div>

            <h1>Fund AI</h1>

            <p>
              Join our community and support great ideas.
            </p>

          </div>

          {/* FORM */}
          <div className="form-section">

            <h2>Create Account</h2>

            <p className="subtitle">
              Create your Fund AI account
            </p>

            <form onSubmit={handleSignup}>

              {/* NAME */}

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

              {/* EMAIL */}

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

              {/* PHONE */}

              <label>Phone</label>

              <input
                type="tel"
                placeholder="Enter your phone number"
                value={signupData.phone}
                onChange={(e) =>
                  setSignupData({
                    ...signupData,
                    phone: e.target.value,
                  })
                }
              />

              {/* PASSWORD */}

              <label>Password</label>

              <input
                type="password"
                placeholder="Create a password"
                value={signupData.password}
                onChange={(e) =>
                  setSignupData({
                    ...signupData,
                    password: e.target.value,
                  })
                }
                required
              />

              {/* ========================= */}
              {/* ROLE SELECTION */}
              {/* ========================= */}

              <label className="role-title">
                Register as
              </label>

              <div className="role-options">

                {/* DONOR */}

                <label
                  className={
                    signupData.role === "USER"
                      ? "role-option active"
                      : "role-option"
                  }
                >

                  <input
                    type="radio"
                    name="role"
                    value="USER"
                    checked={signupData.role === "USER"}
                    onChange={(e) =>
                      setSignupData({
                        ...signupData,
                        role: e.target.value,
                      })
                    }
                  />

                  <div className="role-content">

                    <strong>
                      Donor
                    </strong>

                    <small>
                      Support campaigns
                    </small>

                  </div>

                </label>

                {/* CAMPAIGNER */}

                <label
                  className={
                    signupData.role === "CREATOR"
                      ? "role-option active"
                      : "role-option"
                  }
                >

                  <input
                    type="radio"
                    name="role"
                    value="CREATOR"
                    checked={signupData.role === "CREATOR"}
                    onChange={(e) =>
                      setSignupData({
                        ...signupData,
                        role: e.target.value,
                      })
                    }
                  />

                  <div className="role-content">

                    <strong>
                      Campaigner
                    </strong>

                    <small>
                      Create fundraising campaigns
                    </small>

                  </div>

                </label>

              </div>

              {/* MESSAGE */}

              {message && (
                <div className={`message ${messageType}`}>
                  {message}
                </div>
              )}

              {/* BUTTON */}

              <button type="submit">
                Create Account
              </button>

            </form>

            <p className="switch">
              Already have an account?

              <span
                onClick={() => {
                  setPage("login");
                  setMessage("");
                  setMessageType("");
                }}
              >
                Login
              </span>
            </p>

          </div>

        </div>

      </div>
    );
  }

  // =========================
  // DONOR DASHBOARD
  // =========================

  if (user?.role === "USER") {
    return (
      <div className="dashboard">

        <nav className="navbar">

          <div className="nav-brand">

            <div className="small-logo">
              F
            </div>

            <strong>
              Fund AI
            </strong>

          </div>

          <div className="nav-user">

            <span>
              {user?.email}
            </span>

            <button
              className="logout"
              onClick={handleLogout}
            >
              Logout
            </button>

          </div>

        </nav>

        <main className="dashboard-main">

          <h1>
            Welcome Donor 👋
          </h1>

          <p className="dashboard-subtitle">
            Discover campaigns and support meaningful ideas.
          </p>

          <div className="dashboard-cards">

            <div className="dashboard-card">
              <h3>
                🔎 Explore Campaigns
              </h3>

              <p>
                Find campaigns that you want to support.
              </p>
            </div>

            <div className="dashboard-card">
              <h3>
                💰 My Donations
              </h3>

              <p>
                View your donation history.
              </p>
            </div>

            <div className="dashboard-card">
              <h3>
                ❤️ Supported Campaigns
              </h3>

              <p>
                Track campaigns you have supported.
              </p>
            </div>

          </div>

        </main>

      </div>
    );
  }

  // =========================
  // CAMPAIGNER DASHBOARD
  // =========================

  if (user?.role === "CREATOR") {
    return (
      <div className="dashboard">

        <nav className="navbar">

          <div className="nav-brand">

            <div className="small-logo">
              F
            </div>

            <strong>
              Fund AI
            </strong>

          </div>

          <div className="nav-user">

            <span>
              {user?.email}
            </span>

            <button
              className="logout"
              onClick={handleLogout}
            >
              Logout
            </button>

          </div>

        </nav>

        <main className="dashboard-main">

          <h1>
            Welcome Campaigner 🚀
          </h1>

          <p className="dashboard-subtitle">
            Create and manage your fundraising campaigns.
          </p>

          <div className="dashboard-cards">

            <div className="dashboard-card">
              <h3>
                ➕ Create Campaign
              </h3>

              <p>
                Start a new fundraising campaign.
              </p>
            </div>

            <div className="dashboard-card">
              <h3>
                📢 My Campaigns
              </h3>

              <p>
                View and manage your campaigns.
              </p>
            </div>

            <div className="dashboard-card">
              <h3>
                💰 Campaign Donations
              </h3>

              <p>
                Track donations received for your campaigns.
              </p>
            </div>

          </div>

        </main>

      </div>
    );
  }

  // =========================
  // ADMIN DASHBOARD
  // =========================

  if (user?.role === "ADMIN") {
    return (
      <div className="dashboard">

        <nav className="navbar">

          <div className="nav-brand">

            <div className="small-logo">
              F
            </div>

            <strong>
              Fund AI Admin
            </strong>

          </div>

          <div className="nav-user">

            <span>
              {user?.email}
            </span>

            <button
              className="logout"
              onClick={handleLogout}
            >
              Logout
            </button>

          </div>

        </nav>

        <main className="dashboard-main">

          <h1>
            Welcome Admin 🛡️
          </h1>

          <p className="dashboard-subtitle">
            Manage the Fund AI platform.
          </p>

          <div className="dashboard-cards">

            <div className="dashboard-card">
              <h3>
                👥 Users
              </h3>

              <p>
                Manage registered users.
              </p>
            </div>

            <div className="dashboard-card">
              <h3>
                📢 Campaigns
              </h3>

              <p>
                Manage fundraising campaigns.
              </p>
            </div>

            <div className="dashboard-card">
              <h3>
                💳 Payments
              </h3>

              <p>
                Monitor donations and payments.
              </p>
            </div>

          </div>

        </main>

      </div>
    );
  }

  // =========================
  // FALLBACK
  // =========================

  return (
    <div className="page">

      <div className="auth-box">

        <div className="form-section">

          <h2>
            Unknown User Role
          </h2>

          <p>
            Please contact the administrator.
          </p>

          <button onClick={handleLogout}>
            Back to Login
          </button>

        </div>

      </div>

    </div>
  );
}

export default App;