import { useEffect, useState } from "react";
import api from "./api";
import "./App.css";

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
    role: "DONOR",
  });

  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");
  const [loading, setLoading] = useState(false);

  const [user, setUser] = useState(null);

  // Campaigner Form & State
  const [campaignForm, setCampaignForm] = useState({
    title: "",
    description: "",
    goal_amount: "",
    category: "Education",
    start_date: "",
    end_date: "",
    image_url: "",
  });
  const [campaignFormLoading, setCampaignFormLoading] = useState(false);
  const [campaignFormError, setCampaignFormError] = useState("");
  const [campaignerTab, setCampaignerTab] = useState("overview");
  const [receivedDonations, setReceivedDonations] = useState([]);
  const [editingCampaign, setEditingCampaign] = useState(null);
  const [editForm, setEditForm] = useState({
    title: "",
    description: "",
    goal_amount: "",
    category: "Education",
  });
  const [editLoading, setEditLoading] = useState(false);

  // Donor dashboard & Campaign API state (Phase 15 Hardening)
  const [donorSection, setDonorSection] = useState("overview");
  const [campaignSearch, setCampaignSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [sortOption, setSortOption] = useState("newest");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(10);
  const [paginationMeta, setPaginationMeta] = useState({ total: 0, total_pages: 1 });

  const [savedCampaignIds, setSavedCampaignIds] = useState([]);
  const [savedCampaignsData, setSavedCampaignsData] = useState([]);
  const [savedCampaignsLoading, setSavedCampaignsLoading] = useState(false);
  const [savedCampaignsError, setSavedCampaignsError] = useState("");
  const [donorCampaigns, setDonorCampaigns] = useState([]);
  const [campaignsLoading, setCampaignsLoading] = useState(false);
  const [campaignsError, setCampaignsError] = useState("");
  const [myDonations, setMyDonations] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notificationsLoading, setNotificationsLoading] = useState(false);
  const [notificationsError, setNotificationsError] = useState("");

  // Comments state
  const [comments, setComments] = useState([]);
  const [commentsLoading, setCommentsLoading] = useState(false);
  const [commentsError, setCommentsError] = useState("");
  const [commentText, setCommentText] = useState("");
  const [postingComment, setPostingComment] = useState(false);
  const [editingCommentId, setEditingCommentId] = useState(null);
  const [editCommentText, setEditCommentText] = useState("");
  const [savingCampaignId, setSavingCampaignId] = useState(null);

  // Modals
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [donationModalOpen, setDonationModalOpen] = useState(false);
  const [donationAmount, setDonationAmount] = useState("");
  const [donating, setDonating] = useState(false);

  // Admin Dashboard State
  const [adminTab, setAdminTab] = useState("overview");
  const [adminReports, setAdminReports] = useState(null);
  const [adminUsers, setAdminUsers] = useState([]);
  const [adminCampaigns, setAdminCampaigns] = useState([]);
  const [adminDonations, setAdminDonations] = useState([]);
  const [adminTransactions, setAdminTransactions] = useState([]);
  const [adminAuditLogs, setAdminAuditLogs] = useState([]);
  const [adminLoading, setAdminLoading] = useState(false);

  const [adminUserSearch, setAdminUserSearch] = useState("");
  const [adminUserRoleFilter, setAdminUserRoleFilter] = useState("ALL");
  const [adminUserStatusFilter, setAdminUserStatusFilter] = useState("ALL");

  const [adminCampaignSearch, setAdminCampaignSearch] = useState("");
  const [adminCampaignStatusFilter, setAdminCampaignStatusFilter] = useState("ALL");

  /* ================================
     MESSAGE HELPERS
  ================================= */

  const showMessage = (text, type) => {
    setMessage(text);
    setMessageType(type);
  };

  const clearMessage = () => {
    setMessage("");
    setMessageType("");
  };

  const getCampaignIcon = (category) => {
    const value = (category || "").toLowerCase();
    if (value.includes("education")) return "🎓";
    if (value.includes("medical") || value.includes("health")) return "🏥";
    if (value.includes("food")) return "🍲";
    if (value.includes("emergency") || value.includes("relief")) return "🤝";
    if (value.includes("children") || value.includes("child")) return "🧒";
    if (value.includes("skill")) return "💡";
    if (value.includes("community")) return "🏘️";
    return "💚";
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount || 0);
  };

  const progressPercentage = (raised, goal) => {
    if (!goal || goal <= 0) return 0;
    return Math.min(Math.round((raised / goal) * 100), 100);
  };

  /* ================================
     API FETCHERS (Phase 15 Search, Sort, Filter, Paginate)
  ================================= */

  const fetchCampaigns = async (overrideParams = {}) => {
    setCampaignsLoading(true);
    setCampaignsError("");

    const searchParam = overrideParams.search !== undefined ? overrideParams.search : campaignSearch;
    const categoryParam = overrideParams.category !== undefined ? overrideParams.category : categoryFilter;
    const sortParam = overrideParams.sort !== undefined ? overrideParams.sort : sortOption;
    const pageParam = overrideParams.page !== undefined ? overrideParams.page : currentPage;

    try {
      const params = {
        page: pageParam,
        page_size: pageSize,
        sort: sortParam,
      };

      if (searchParam) params.search = searchParam;
      if (categoryParam) params.category = categoryParam;

      const response = await api.get("/campaigns/", { params });
      const rawData = response.data.items || (Array.isArray(response.data) ? response.data : []);

      if (response.data.total !== undefined) {
        setPaginationMeta({
          total: response.data.total,
          total_pages: response.data.total_pages,
        });
      } else {
        setPaginationMeta({
          total: rawData.length,
          total_pages: 1,
        });
      }

      const campaigns = rawData.map((campaign) => ({
        id: campaign.campaign_id,
        title: campaign.title,
        category: campaign.category,
        description: campaign.description,
        raised: Number(campaign.collected_amount || 0),
        goal: Number(campaign.goal_amount || 0),
        donors: 0,
        status: campaign.status,
        icon: getCampaignIcon(campaign.category),
        creator_id: campaign.creator_id,
        start_date: campaign.start_date,
        end_date: campaign.end_date,
      }));

      setDonorCampaigns(campaigns);
    } catch (error) {
      console.error("CAMPAIGNS ERROR:", error);
      setCampaignsError(getErrorMessage(error, "Unable to load campaigns."));
    } finally {
      setCampaignsLoading(false);
    }
  };

  const fetchSavedCampaigns = async () => {
    setSavedCampaignsLoading(true);
    setSavedCampaignsError("");
    try {
      const res = await api.get("/saved-campaigns/");
      if (res.data && res.data.data) {
        const ids = res.data.data.map((item) => item.campaign?.campaign_id || item.campaign_id).filter(Boolean);
        setSavedCampaignIds(ids);
        setSavedCampaignsData(res.data.data);
      } else {
        setSavedCampaignIds([]);
        setSavedCampaignsData([]);
      }
    } catch (error) {
      console.error("SAVED CAMPAIGNS ERROR:", error);
      setSavedCampaignsError(getErrorMessage(error, "Unable to load saved campaigns."));
    } finally {
      setSavedCampaignsLoading(false);
    }
  };

  const fetchMyDonations = async () => {
    try {
      const res = await api.get("/donations/my");
      setMyDonations(res.data || []);
    } catch (error) {
      console.error("MY DONATIONS ERROR:", error);
      setMyDonations([]);
    }
  };

  const fetchReceivedDonations = async () => {
    try {
      const res = await api.get("/donations/received");
      setReceivedDonations(res.data || []);
    } catch (error) {
      console.error("RECEIVED DONATIONS ERROR:", error);
      setReceivedDonations([]);
    }
  };

  const fetchComments = async (campaignId) => {
    setCommentsLoading(true);
    setCommentsError("");
    try {
      const res = await api.get(`/comments/${campaignId}`);
      setComments(res.data || []);
    } catch (error) {
      console.error("COMMENTS ERROR:", error);
      setCommentsError(getErrorMessage(error, "Unable to load comments."));
    } finally {
      setCommentsLoading(false);
    }
  };

  const postComment = async (campaignId, text) => {
    setPostingComment(true);
    try {
      const res = await api.post("/comments/", { campaign_id: campaignId, comment_text: text });
      setComments((prev) => [res.data, ...prev]);
      return res.data;
    } catch (error) {
      console.error("POST COMMENT ERROR:", error);
      throw error;
    } finally {
      setPostingComment(false);
    }
  };

  const updateComment = async (commentId, text) => {
    try {
      const res = await api.put(`/comments/${commentId}`, { comment_text: text });
      setComments((prev) => prev.map((c) => (c.comment_id === commentId ? res.data : c)));
      return res.data;
    } catch (error) {
      console.error("UPDATE COMMENT ERROR:", error);
      throw error;
    }
  };

  const deleteComment = async (commentId) => {
    try {
      await api.delete(`/comments/${commentId}`);
      setComments((prev) => prev.filter((c) => c.comment_id !== commentId));
    } catch (error) {
      console.error("DELETE COMMENT ERROR:", error);
      throw error;
    }
  };

  const markNotificationRead = async (notificationId) => {
    try {
      const res = await api.patch(`/notifications/${notificationId}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.notification_id === notificationId ? res.data : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
      return res.data;
    } catch (error) {
      console.error("MARK NOTIFICATION READ ERROR:", error);
      throw error;
    }
  };

  const markAllNotificationsRead = async () => {
    try {
      await api.patch("/notifications/read-all");
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error("MARK ALL NOTIFICATIONS READ ERROR:", error);
      throw error;
    }
  };

  const fetchUnreadCount = async () => {
    try {
      const res = await api.get("/notifications/unread-count");
      setUnreadCount(res.data?.unread_count || 0);
    } catch (error) {
      console.error("UNREAD COUNT ERROR:", error);
    }
  };

  const fetchNotifications = async () => {
    setNotificationsLoading(true);
    setNotificationsError("");
    try {
      const res = await api.get("/notifications/");
      setNotifications(res.data || []);
      fetchUnreadCount();
    } catch (error) {
      console.error("NOTIFICATIONS ERROR:", error);
      setNotificationsError(getErrorMessage(error, "Unable to load notifications."));
    } finally {
      setNotificationsLoading(false);
    }
  };

  const fetchAdminData = async () => {
    setAdminLoading(true);
    try {
      const [reportsRes, usersRes, campaignsRes, donationsRes, transactionsRes, auditLogsRes] = await Promise.all([
        api.get("/admin/reports").catch(() => null),
        api.get("/admin/users").catch(() => null),
        api.get("/admin/campaigns").catch(() => null),
        api.get("/admin/donations").catch(() => null),
        api.get("/admin/transactions").catch(() => null),
        api.get("/admin/audit-logs").catch(() => null),
      ]);

      if (reportsRes?.data?.data) setAdminReports(reportsRes.data.data);
      if (usersRes?.data) setAdminUsers(usersRes.data);
      if (campaignsRes?.data) setAdminCampaigns(campaignsRes.data);
      if (donationsRes?.data) setAdminDonations(donationsRes.data);
      if (transactionsRes?.data) setAdminTransactions(transactionsRes.data);
      if (auditLogsRes?.data) setAdminAuditLogs(auditLogsRes.data);
    } catch (error) {
      console.error("ADMIN DATA ERROR:", error);
    } finally {
      setAdminLoading(false);
    }
  };

  const toggleUserActive = async (targetUser) => {
    if (targetUser.user_id === user?.user_id) {
      setMessage("Admin cannot deactivate their own active account.");
      setMessageType("error");
      return;
    }
    const actionText = targetUser.is_active !== false ? "deactivate" : "activate";
    if (!window.confirm(`Are you sure you want to ${actionText} user '${targetUser.email}'?`)) return;

    try {
      if (targetUser.is_active !== false) {
        await api.patch(`/admin/users/${targetUser.user_id}/deactivate`);
        setMessage(`User ${targetUser.email} deactivated successfully.`);
        setMessageType("success");
      } else {
        await api.patch(`/admin/users/${targetUser.user_id}/activate`);
        setMessage(`User ${targetUser.email} activated successfully.`);
        setMessageType("success");
      }
      fetchAdminData();
    } catch (error) {
      console.error("TOGGLE USER ACTIVE ERROR:", error);
      setMessage(getErrorMessage(error, "Failed to update user status."));
      setMessageType("error");
    }
  };

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedRole = localStorage.getItem("role");
    const savedName = localStorage.getItem("name");
    const savedEmail = localStorage.getItem("email");
    const savedUserId = localStorage.getItem("user_id");

    if (savedToken && savedRole) {
      const normalizedRole = savedRole.toUpperCase();
      setUser({
        user_id: Number(savedUserId || 0),
        name: savedName || "User",
        email: savedEmail || "",
        role: normalizedRole,
        access_token: savedToken,
      });

      if (normalizedRole === "DONOR") setPage("donor");
      else if (normalizedRole === "CAMPAIGNER") setPage("campaigner");
      else if (normalizedRole === "ADMIN") setPage("admin");
      else setPage("login");
    } else {
      setPage("login");
    }
  }, []);

  useEffect(() => {
    if (page === "donor" || page === "campaigner") {
      fetchCampaigns();
      if (page === "donor") {
        fetchSavedCampaigns();
        fetchMyDonations();
        fetchNotifications();
      } else if (page === "campaigner") {
        fetchReceivedDonations();
        fetchNotifications();
      }
    } else if (page === "admin") {
      fetchAdminData();
    }
  }, [page]);

  useEffect(() => {
    if (selectedCampaign) {
      fetchComments(selectedCampaign.id);
    } else {
      setComments([]);
    }
  }, [selectedCampaign]);

  /* ================================
     ERROR HANDLER (Phase 15 Error Improvements)
  ================================= */

  const getErrorMessage = (error, defaultMessage) => {
    if (!error.response) {
      if (error.code === "ECONNABORTED" || error.message?.toLowerCase().includes("timeout")) {
        return "The campaign server is taking too long to respond. Please try again.";
      }
      if (error.request) {
        return "Unable to connect to the backend. Please check that the backend is running and CORS is configured.";
      }
      return error.message || defaultMessage;
    }

    const detail = error.response.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((item) => item.msg).join(", ");
    if (error.response.status === 401) return "Session expired or invalid credentials. Please log in again.";
    if (error.response.status === 403) return "Access denied. You do not have permission for this action.";
    if (error.response.status === 404) return "Requested resource not found.";
    if (error.response.status === 422) return "Validation error. Please check your inputs.";
    if (error.response.status === 500) return "Server error. Check backend logs.";
    return defaultMessage;
  };

  /* ================================
     ACTIONS
  ================================= */

  const handleLogin = async (e) => {
    e.preventDefault();
    clearMessage();
    setLoading(true);

    try {
      const response = await api.post("/auth/login", {
        email: loginData.email.trim(),
        password: loginData.password,
      });

      const data = response.data;

      // Defensive: if server returns is_active=false, block login on frontend too
      if (data.is_active === false) {
        showMessage("Your account has been deactivated. Please contact admin.", "error");
        setLoading(false);
        return;
      }

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("role", data.role);
      localStorage.setItem("user_id", data.user_id);
      localStorage.setItem("name", data.name);
      localStorage.setItem("email", data.email);

      setUser(data);
      showMessage(`Welcome back, ${data.name}!`, "success");

      setTimeout(() => {
        if (data.role === "DONOR") setPage("donor");
        else if (data.role === "CAMPAIGNER") setPage("campaigner");
        else if (data.role === "ADMIN") setPage("admin");
      }, 600);
    } catch (error) {
      console.error("LOGIN ERROR:", error);
      // Show specific 401 message for deactivated accounts
      if (error.response?.status === 401) {
        const detail = error.response?.data?.detail || "";
        if (detail.toLowerCase().includes("deactivated")) {
          showMessage("Your account has been deactivated. Contact admin to restore access.", "error");
        } else {
          showMessage("Invalid email or password.", "error");
        }
      } else {
        showMessage(getErrorMessage(error, "Login failed."), "error");
      }
    } finally {
      setLoading(false);
    }
  };


  const handleSignup = async (e) => {
    e.preventDefault();
    clearMessage();
    setLoading(true);

    try {
      await api.post("/auth/signup", {
        name: signupData.name.trim(),
        email: signupData.email.trim(),
        password: signupData.password,
        phone: signupData.phone.trim() || undefined,
        role: signupData.role,
      });

      showMessage("Account created successfully! Please sign in.", "success");
      setLoginData({
        email: signupData.email.trim(),
        password: "",
      });

      setSignupData({
        name: "",
        email: "",
        password: "",
        phone: "",
        role: "DONOR",
      });

      setTimeout(() => {
        setPage("login");
        clearMessage();
      }, 1000);
    } catch (error) {
      console.error("SIGNUP ERROR:", error);
      showMessage(getErrorMessage(error, "Signup failed."), "error");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
    setLoginData({ email: "", password: "" });
    clearMessage();
    setPage("login");
  };

  const handleCreateCampaign = async (e) => {
    e.preventDefault();
    clearMessage();
    setCampaignFormLoading(true);
    setCampaignFormError("");

    try {
      const trimmedTitle = campaignForm.title.trim();
      const trimmedDescription = campaignForm.description.trim();
      const goalAmount = Number(campaignForm.goal_amount);

      if (!trimmedTitle || !trimmedDescription || !campaignForm.category) {
        throw new Error("Please fill in all required campaign details.");
      }

      if (!Number.isFinite(goalAmount) || goalAmount <= 0) {
        throw new Error("Goal amount must be greater than 0.");
      }

      await api.post("/campaigns/", {
        title: trimmedTitle,
        description: trimmedDescription,
        goal_amount: goalAmount,
        category: campaignForm.category,
        start_date: campaignForm.start_date || undefined,
        end_date: campaignForm.end_date || undefined,
      });

      setCampaignForm({
        title: "",
        description: "",
        goal_amount: "",
        category: "Education",
        start_date: "",
        end_date: "",
        image_url: "",
      });

      showMessage("Campaign submitted successfully! Status is PENDING for admin review.", "success");
      setCampaignerTab("my-campaigns");
      await fetchCampaigns();
    } catch (error) {
      console.error("CREATE CAMPAIGN ERROR:", error);
      setCampaignFormError(getErrorMessage(error, "Unable to create campaign."));
    } finally {
      setCampaignFormLoading(false);
    }
  };

  const handleOpenEdit = (campaign) => {
    setEditingCampaign(campaign);
    setEditForm({
      title: campaign.title,
      description: campaign.description,
      goal_amount: campaign.goal,
      category: campaign.category,
    });
  };

  const handleUpdateCampaign = async (e) => {
    e.preventDefault();
    if (!editingCampaign) return;

    setEditLoading(true);
    try {
      await api.put(`/campaigns/${editingCampaign.id}`, {
        title: editForm.title.trim(),
        description: editForm.description.trim(),
        goal_amount: Number(editForm.goal_amount),
        category: editForm.category,
      });

      showMessage("Campaign updated successfully!", "success");
      setEditingCampaign(null);
      fetchCampaigns();
    } catch (error) {
      console.error("UPDATE CAMPAIGN ERROR:", error);
      showMessage(getErrorMessage(error, "Failed to update campaign."), "error");
    } finally {
      setEditLoading(false);
    }
  };

  const handleDeleteCampaign = async (campaignId, title) => {
    if (!window.confirm(`Are you sure you want to delete "${title}"?`)) return;

    try {
      await api.delete(`/campaigns/${campaignId}`);
      showMessage(`Campaign "${title}" was deleted.`, "success");
      fetchCampaigns();
    } catch (error) {
      console.error("DELETE CAMPAIGN ERROR:", error);
      showMessage(getErrorMessage(error, "Failed to delete campaign."), "error");
    }
  };

  const toggleSavedCampaign = async (campaignId) => {
    const isSaved = savedCampaignIds.includes(campaignId);
    setSavingCampaignId(campaignId);
    try {
      if (isSaved) {
        await api.delete(`/saved-campaigns/${campaignId}`);
        setSavedCampaignIds((prev) => prev.filter((id) => id !== campaignId));
        setSavedCampaignsData((prev) => prev.filter((item) => (item.campaign?.campaign_id || item.campaign_id) !== campaignId));
        showMessage("Removed from saved campaigns.", "success");
      } else {
        try {
          const res = await api.post(`/saved-campaigns/${campaignId}`);
          const campaignPayload = res.data?.data?.campaign || { campaign_id: campaignId };
          setSavedCampaignIds((prev) => [...prev, campaignId]);
          setSavedCampaignsData((prev) => [
            { campaign: campaignPayload, saved_at: res.data?.data?.saved_at },
            ...prev,
          ]);
          showMessage("Campaign saved successfully!", "success");
        } catch (err) {
          if (err.response?.status === 409) {
            showMessage("Campaign already saved.", "error");
          } else {
            throw err;
          }
        }
      }
      await fetchSavedCampaigns();
    } catch (error) {
      console.error("TOGGLE SAVE ERROR:", error);
      showMessage(getErrorMessage(error, "Could not update saved campaign."), "error");
    } finally {
      setSavingCampaignId(null);
    }
  };

  const handlePostComment = async (e) => {
    e.preventDefault();
    if (!selectedCampaign) return;
    const text = commentText.trim();
    if (!text) {
      showMessage("Please enter a comment.", "error");
      return;
    }
    setPostingComment(true);
    try {
      await postComment(selectedCampaign.id, text);
      setCommentText("");
      showMessage("Comment posted!", "success");
    } catch (error) {
      showMessage(getErrorMessage(error, "Failed to post comment."), "error");
    } finally {
      setPostingComment(false);
    }
  };

  const handleUpdateComment = async (commentId) => {
    const text = editCommentText.trim();
    if (!text) {
      showMessage("Comment cannot be empty.", "error");
      return;
    }
    try {
      await updateComment(commentId, text);
      setEditingCommentId(null);
      setEditCommentText("");
      showMessage("Comment updated!", "success");
    } catch (error) {
      showMessage(getErrorMessage(error, "Failed to update comment."), "error");
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm("Delete this comment?")) return;
    try {
      await deleteComment(commentId);
      showMessage("Comment deleted.", "success");
    } catch (error) {
      showMessage(getErrorMessage(error, "Failed to delete comment."), "error");
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsRead();
      showMessage("All notifications marked as read.", "success");
    } catch (error) {
      showMessage(getErrorMessage(error, "Failed to mark all as read."), "error");
    }
  };

  const handleMarkRead = async (notificationId) => {
    try {
      await markNotificationRead(notificationId);
      showMessage("Notification marked as read.", "success");
    } catch (error) {
      showMessage(getErrorMessage(error, "Failed to mark as read."), "error");
    }
  };

  const formatRelativeTime = (isoDate) => {
    if (!isoDate) return "Just now";
    const date = new Date(isoDate);
    if (isNaN(date.getTime())) return "Recently";
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    if (diffSec < 60) return "Just now";
    if (diffMin < 60) return `${diffMin} minute${diffMin === 1 ? "" : "s"} ago`;
    if (diffHour < 24) return `${diffHour} hour${diffHour === 1 ? "" : "s"} ago`;
    if (diffDay < 7) return `${diffDay} day${diffDay === 1 ? "" : "s"} ago`;
    return date.toLocaleDateString();
  };

  const handleDonateSubmit = async (e) => {
    e.preventDefault();
    if (!selectedCampaign) return;

    const amount = Number(donationAmount);
    if (!amount || amount <= 0) {
      showMessage("Please enter a valid donation amount greater than 0.", "error");
      return;
    }

    setDonating(true);
    try {
      const paymentRes = await api.post("/payments/create", {
        campaign_id: selectedCampaign.id,
        amount: amount,
      });

      const paymentReference = paymentRes.data?.data?.payment_reference;

      await api.post("/payments/verify", {
        payment_reference: paymentReference,
        campaign_id: selectedCampaign.id,
        amount: amount,
      });

      showMessage(`Thank you! Your donation of ${formatCurrency(amount)} was successful!`, "success");
      setDonationModalOpen(false);
      setSelectedCampaign(null);
      setDonationAmount("");

      fetchCampaigns();
      fetchMyDonations();
      fetchNotifications();
    } catch (error) {
      console.error("DONATION ERROR:", error);
      showMessage(getErrorMessage(error, "Donation process failed."), "error");
    } finally {
      setDonating(false);
    }
  };

  const handleAdminApprove = async (campaignId) => {
    if (!window.confirm("Are you sure you want to approve this campaign?")) return;
    try {
      await api.patch(`/admin/campaigns/${campaignId}/approve`);
      showMessage("Campaign approved successfully!", "success");
      fetchAdminData();
    } catch (error) {
      showMessage(getErrorMessage(error, "Failed to approve campaign."), "error");
    }
  };

  const handleAdminReject = async (campaignId) => {
    if (!window.confirm("Are you sure you want to reject this campaign?")) return;
    try {
      await api.patch(`/admin/campaigns/${campaignId}/reject`);
      showMessage("Campaign rejected.", "success");
      fetchAdminData();
    } catch (error) {
      showMessage(getErrorMessage(error, "Failed to reject campaign."), "error");
    }
  };

  /* ================================
     LOGIN PAGE
  ================================= */

  if (page === "login") {
    return (
      <div className="auth-page">
        <div className="auth-wrapper">
          <div className="auth-brand">
            <div className="brand-logo">F</div>
            <h1>Fund<span>AI</span></h1>
            <p>Empowering ideas.<br />Supporting dreams.</p>
            <div className="brand-line"></div>
            <div className="brand-feature"><span>✓</span> Secure & trusted platform</div>
            <div className="brand-feature"><span>✓</span> Support meaningful causes</div>
            <div className="brand-feature"><span>✓</span> Make an impact together</div>
          </div>

          <div className="auth-form-area">
            <div className="auth-form">
              <div className="mobile-logo">F</div>
              <h2>Welcome Back</h2>
              <p className="form-subtitle">Sign in to continue to Fund AI</p>

              {message && (
                <div className={`alert ${messageType === "error" ? "alert-error" : "alert-success"}`}>
                  {message}
                </div>
              )}

              <form onSubmit={handleLogin}>
                <div className="input-group">
                  <label>Email Address</label>
                  <div className="input-wrapper">
                    <span className="input-icon">✉</span>
                    <input
                      type="email"
                      placeholder="Enter your email"
                      value={loginData.email}
                      onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                      required
                    />
                  </div>
                </div>

                <div className="input-group">
                  <label>Password</label>
                  <div className="input-wrapper">
                    <span className="input-icon">🔒</span>
                    <input
                      type="password"
                      placeholder="Enter your password"
                      value={loginData.password}
                      onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                      required
                    />
                  </div>
                </div>

                <button type="submit" className="main-btn" disabled={loading}>
                  {loading ? "Signing in..." : "Sign In"}
                </button>
              </form>

              <div className="divider"><span>OR</span></div>

              <p className="switch-text">
                Don't have an account?{" "}
                <button
                  type="button"
                  onClick={() => {
                    clearMessage();
                    setPage("signup");
                  }}
                >
                  Create Account
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  /* ================================
     SIGNUP PAGE
  ================================= */

  if (page === "signup") {
    return (
      <div className="auth-page">
        <div className="auth-wrapper">
          <div className="auth-brand">
            <div className="brand-logo">F</div>
            <h1>Fund<span>AI</span></h1>
            <p>Turn your ideas<br />into real impact.</p>
            <div className="brand-line"></div>
            <div className="brand-feature"><span>✓</span> Create fundraising campaigns</div>
            <div className="brand-feature"><span>✓</span> Support people in need</div>
            <div className="brand-feature"><span>✓</span> Build a better community</div>
          </div>

          <div className="auth-form-area">
            <div className="auth-form signup-form">
              <div className="mobile-logo">F</div>
              <h2>Create Account</h2>
              <p className="form-subtitle">Join Fund AI and make a difference</p>

              {message && (
                <div className={`alert ${messageType === "error" ? "alert-error" : "alert-success"}`}>
                  {message}
                </div>
              )}

              <form onSubmit={handleSignup}>
                <div className="input-group">
                  <label>Full Name</label>
                  <div className="input-wrapper">
                    <span className="input-icon">👤</span>
                    <input
                      type="text"
                      placeholder="Enter your full name"
                      value={signupData.name}
                      onChange={(e) => setSignupData({ ...signupData, name: e.target.value })}
                      required
                    />
                  </div>
                </div>

                <div className="input-group">
                  <label>Email Address</label>
                  <div className="input-wrapper">
                    <span className="input-icon">✉</span>
                    <input
                      type="email"
                      placeholder="Enter your email"
                      value={signupData.email}
                      onChange={(e) => setSignupData({ ...signupData, email: e.target.value })}
                      required
                    />
                  </div>
                </div>

                <div className="input-group">
                  <label>Phone Number</label>
                  <div className="input-wrapper">
                    <span className="input-icon">☎</span>
                    <input
                      type="tel"
                      placeholder="Enter phone number"
                      value={signupData.phone}
                      onChange={(e) => setSignupData({ ...signupData, phone: e.target.value })}
                    />
                  </div>
                </div>

                <div className="input-group">
                  <label>Password</label>
                  <div className="input-wrapper">
                    <span className="input-icon">🔒</span>
                    <input
                      type="password"
                      placeholder="Create a password"
                      value={signupData.password}
                      onChange={(e) => setSignupData({ ...signupData, password: e.target.value })}
                      minLength="6"
                      required
                    />
                  </div>
                </div>

                <div className="input-group">
                  <label>Account Type</label>
                  <div className="role-options">
                    <button
                      type="button"
                      className={signupData.role === "DONOR" ? "role-btn active" : "role-btn"}
                      onClick={() => setSignupData({ ...signupData, role: "DONOR" })}
                    >
                      ❤️ Donor
                    </button>

                    <button
                      type="button"
                      className={signupData.role === "CAMPAIGNER" ? "role-btn active" : "role-btn"}
                      onClick={() => setSignupData({ ...signupData, role: "CAMPAIGNER" })}
                    >
                      🚀 Campaigner
                    </button>
                  </div>
                </div>

                <button type="submit" className="main-btn" disabled={loading}>
                  {loading ? "Creating Account..." : "Create Account"}
                </button>
              </form>

              <div className="divider"><span>OR</span></div>

              <p className="switch-text">
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => {
                    clearMessage();
                    setPage("login");
                  }}
                >
                  Sign In
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  /* ================================
     DONOR PAGE (PHASE 15 ENHANCED SEARCH, SORT, FILTER & PAGINATION)
  ================================= */

  if (page === "donor") {
    const activeCampaigns = donorCampaigns.filter((c) => c.status === "ACTIVE" || c.status === "COMPLETED");

    const totalDonatedAmount = myDonations.reduce((acc, d) => acc + (d.amount || 0), 0);
    const uniqueCampaignsSupported = new Set(myDonations.map((d) => d.campaign_id)).size;

const donorNavItems = [
      { id: "overview", icon: "🏠", label: "Dashboard" },
      { id: "campaigns", icon: "🔍", label: "Explore Campaigns" },
      { id: "donations", icon: "💰", label: "My Donations" },
      { id: "saved", icon: "❤️", label: "Saved Campaigns" },
      { id: "notifications", icon: "🔔", label: "Notifications", badge: unreadCount },
      { id: "profile", icon: "👤", label: "My Profile" },
    ];

    return (
      <div className="dashboard-page donor-dashboard-page">
        <nav className="dashboard-nav donor-top-nav">
          <div className="dashboard-logo">
            <div>F</div>
            <span>FundAI</span>
          </div>

          <div className="dashboard-user">
            <div className="top-user-info">
              <div className="top-user-avatar">
                {(user?.name || "D").charAt(0).toUpperCase()}
              </div>
              <span>{user?.name}</span>
            </div>
            <button onClick={handleLogout}>Logout</button>
          </div>
        </nav>

        <div className="donor-layout">
          <aside className="donor-sidebar">
            <div className="sidebar-role">
              <span className="sidebar-role-dot"></span>
              DONOR ACCOUNT
            </div>

            <div className="sidebar-nav">
              {donorNavItems.map((item) => (
                <button
                  key={item.id}
                  className={donorSection === item.id ? "sidebar-nav-item active" : "sidebar-nav-item"}
                  onClick={() => setDonorSection(item.id)}
                >
                  <span className="sidebar-icon">{item.icon}</span>
                  <span>{item.label}</span>
                  {item.badge > 0 && <span className="nav-badge">{item.badge}</span>}
                </button>
              ))}
            </div>

            <div className="sidebar-help">
              <div className="sidebar-help-icon">💚</div>
              <strong>Make an impact</strong>
              <p>Every contribution can help a campaign move closer to its goal.</p>
            </div>
          </aside>

          <main className="donor-main-content">
            {donorSection === "overview" && (
              <>
                <div className="donor-page-heading">
                  <div>
                    <span className="section-kicker">DONOR DASHBOARD</span>
                    <h1>Welcome, {user?.name} 👋</h1>
                    <p>Discover meaningful campaigns and support causes that matter.</p>
                  </div>
                  <button className="primary-action-btn" onClick={() => setDonorSection("campaigns")}>
                    Explore Campaigns
                  </button>
                </div>

                <section className="donor-stat-grid">
                  <div className="donor-stat-card">
                    <div className="stat-icon">💰</div>
                    <div>
                      <span>Total Donated</span>
                      <strong>{formatCurrency(totalDonatedAmount)}</strong>
                      <small>Across all donations</small>
                    </div>
                  </div>

                  <div className="donor-stat-card">
                    <div className="stat-icon">❤️</div>
                    <div>
                      <span>Campaigns Supported</span>
                      <strong>{uniqueCampaignsSupported}</strong>
                      <small>Causes you have supported</small>
                    </div>
                  </div>

                  <div className="donor-stat-card">
                    <div className="stat-icon">📊</div>
                    <div>
                      <span>Total Donations</span>
                      <strong>{myDonations.length}</strong>
                      <small>Successful contributions</small>
                    </div>
                  </div>

                  <div className="donor-stat-card">
                    <div className="stat-icon">🔖</div>
                    <div>
                      <span>Saved Campaigns</span>
                      <strong>{savedCampaignIds.length}</strong>
                      <small>Campaigns you want to revisit</small>
                    </div>
                  </div>

                  <div className="donor-stat-card">
                    <div className="stat-icon">🔔</div>
                    <div>
                      <span>Unread Notifications</span>
                      <strong>{unreadCount}</strong>
                      <small>Waiting for your attention</small>
                    </div>
                  </div>
                </section>

                <section className="donor-section-block">
                  <div className="section-heading-row">
                    <div>
                      <span className="section-kicker">DISCOVER</span>
                      <h2>Recommended Campaigns</h2>
                    </div>
                    <button className="text-action-btn" onClick={() => setDonorSection("campaigns")}>
                      View all →
                    </button>
                  </div>

                  <div className="campaign-card-grid">
                    {activeCampaigns.slice(0, 3).map((campaign) => (
                      <div className="campaign-card" key={campaign.id}>
                        <div className="campaign-card-top">
                          <div className="campaign-icon">{campaign.icon}</div>
                          <button
                            className={savedCampaignIds.includes(campaign.id) ? "save-btn saved" : "save-btn"}
                            onClick={() => toggleSavedCampaign(campaign.id)}
                          >
                            {savedCampaignIds.includes(campaign.id) ? "♥" : "♡"}
                          </button>
                        </div>

                        <span className="campaign-category">{campaign.category}</span>
                        <h3>{campaign.title}</h3>
                        <p>{campaign.description}</p>

                        <div className="campaign-amount-row">
                          <strong>{formatCurrency(campaign.raised)}</strong>
                          <span>of {formatCurrency(campaign.goal)}</span>
                        </div>

                        <div className="progress-track">
                          <div
                            className="progress-fill"
                            style={{
                              width: `${progressPercentage(campaign.raised, campaign.goal)}%`,
                            }}
                          ></div>
                        </div>

                        <div className="campaign-meta-row">
                          <span>{progressPercentage(campaign.raised, campaign.goal)}% funded</span>
                          <span>{campaign.status}</span>
                        </div>

                        <button
                          className="campaign-view-btn"
                          onClick={() => setSelectedCampaign(campaign)}
                        >
                          View Campaign
                        </button>
                      </div>
                    ))}
                  </div>
                </section>

                <section className="donor-bottom-grid">
                  <div className="recent-donations-card">
                    <div className="section-heading-row compact">
                      <div>
                        <span className="section-kicker">ACTIVITY</span>
                        <h2>Recent Donations</h2>
                      </div>
                      <button className="text-action-btn" onClick={() => setDonorSection("donations")}>
                        View all →
                      </button>
                    </div>

                    <div className="donation-list">
                      {myDonations.length === 0 ? (
                        <p style={{ color: "#64748b", padding: "12px 0" }}>No donations yet. Explore campaigns to make your first contribution!</p>
                      ) : (
                        myDonations.slice(0, 4).map((donation) => (
                          <div className="donation-row" key={donation.donation_id}>
                            <div className="donation-row-icon">💚</div>
                            <div className="donation-row-info">
                              <strong>Campaign #{donation.campaign_id}</strong>
                              <span>ID: DON-{donation.donation_id}</span>
                            </div>
                            <div className="donation-row-right">
                              <strong>{formatCurrency(donation.amount)}</strong>
                              <span className="status-success">Successful</span>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  <div className="impact-card">
                    <div className="impact-icon">🌱</div>
                    <span className="section-kicker">YOUR IMPACT</span>
                    <h2>Small actions create meaningful change.</h2>
                    <p>Keep supporting verified causes and help campaigns reach the people who need them.</p>
                    <button className="primary-action-btn full-width" onClick={() => setDonorSection("campaigns")}>
                      Find a Campaign
                    </button>
                  </div>
                </section>
              </>
            )}

            {donorSection === "campaigns" && (
              <section className="donor-section-page">
                <div className="donor-page-heading">
                  <div>
                    <span className="section-kicker">CAMPAIGNS</span>
                    <h1>Explore Campaigns</h1>
                    <p>Find a cause you care about and support its fundraising goal.</p>
                  </div>
                </div>

                {/* SEARCH, CATEGORY FILTER, SORT TOOLBAR */}
                <div className="campaign-toolbar" style={{ flexDirection: "column", gap: "12px", alignItems: "stretch" }}>
                  <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
                    <div className="campaign-search" style={{ flex: 1, minWidth: "220px" }}>
                      <span>🔍</span>
                      <input
                        type="text"
                        placeholder="Search campaigns, categories, description..."
                        value={campaignSearch}
                        onChange={(e) => {
                          setCampaignSearch(e.target.value);
                          setCurrentPage(1);
                          fetchCampaigns({ search: e.target.value, page: 1 });
                        }}
                      />
                    </div>

                    <select
                      className="admin-tab-btn"
                      value={categoryFilter}
                      onChange={(e) => {
                        setCategoryFilter(e.target.value);
                        setCurrentPage(1);
                        fetchCampaigns({ category: e.target.value, page: 1 });
                      }}
                      style={{ padding: "8px 14px" }}
                    >
                      <option value="">All Categories</option>
                      <option value="Education">Education</option>
                      <option value="Medical">Medical</option>
                      <option value="Food">Food</option>
                      <option value="Emergency">Emergency</option>
                      <option value="Community">Community</option>
                      <option value="Children">Children</option>
                    </select>

                    <select
                      className="admin-tab-btn"
                      value={sortOption}
                      onChange={(e) => {
                        setSortOption(e.target.value);
                        fetchCampaigns({ sort: e.target.value });
                      }}
                      style={{ padding: "8px 14px" }}
                    >
                      <option value="newest">Sort: Newest</option>
                      <option value="oldest">Sort: Oldest</option>
                      <option value="highest_goal">Sort: Highest Goal</option>
                      <option value="highest_progress">Sort: Highest Progress</option>
                    </select>
                  </div>

                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div className="campaign-count">
                      {campaignsLoading
                        ? "Loading..."
                        : `Showing ${activeCampaigns.length} of ${paginationMeta.total} campaigns`}
                    </div>

                    {/* PAGINATION CONTROLS */}
                    {paginationMeta.total_pages > 1 && (
                      <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                        <button
                          className="admin-tab-btn"
                          disabled={currentPage <= 1 || campaignsLoading}
                          onClick={() => {
                            const newPage = currentPage - 1;
                            setCurrentPage(newPage);
                            fetchCampaigns({ page: newPage });
                          }}
                          style={{ padding: "4px 10px", fontSize: "0.85rem" }}
                        >
                          ← Prev
                        </button>

                        <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
                          Page {currentPage} of {paginationMeta.total_pages}
                        </span>

                        <button
                          className="admin-tab-btn"
                          disabled={currentPage >= paginationMeta.total_pages || campaignsLoading}
                          onClick={() => {
                            const newPage = currentPage + 1;
                            setCurrentPage(newPage);
                            fetchCampaigns({ page: newPage });
                          }}
                          style={{ padding: "4px 10px", fontSize: "0.85rem" }}
                        >
                          Next →
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {campaignsLoading && (
                  <div className="empty-state">
                    <div>⏳</div>
                    <h3>Loading campaigns...</h3>
                    <p>Please wait while we fetch campaigns from the server.</p>
                  </div>
                )}

                {!campaignsLoading && campaignsError && (
                  <div className="empty-state">
                    <div>⚠️</div>
                    <h3>Unable to load campaigns</h3>
                    <p style={{ color: "#dc2626", fontWeight: "600" }}>{campaignsError}</p>
                    <button className="primary-action-btn" onClick={() => fetchCampaigns()}>
                      Try Again
                    </button>
                  </div>
                )}

                {!campaignsLoading && !campaignsError && (
                  <div className="campaign-card-grid large">
                    {activeCampaigns.map((campaign) => (
                      <div className="campaign-card" key={campaign.id}>
                        <div className="campaign-card-top">
                          <div className="campaign-icon">{campaign.icon}</div>
                          <button
                            className={savedCampaignIds.includes(campaign.id) ? "save-btn saved" : "save-btn"}
                            onClick={() => toggleSavedCampaign(campaign.id)}
                          >
                            {savedCampaignIds.includes(campaign.id) ? "♥" : "♡"}
                          </button>
                        </div>

                        <span className="campaign-category">{campaign.category}</span>
                        <h3>{campaign.title}</h3>
                        <p>{campaign.description}</p>

                        <div className="campaign-amount-row">
                          <strong>{formatCurrency(campaign.raised)}</strong>
                          <span>of {formatCurrency(campaign.goal)}</span>
                        </div>

                        <div className="progress-track">
                          <div
                            className="progress-fill"
                            style={{
                              width: `${progressPercentage(campaign.raised, campaign.goal)}%`,
                            }}
                          ></div>
                        </div>

                        <div className="campaign-meta-row">
                          <span>{progressPercentage(campaign.raised, campaign.goal)}% funded</span>
                          <span>{campaign.status}</span>
                        </div>

                        <button
                          className="campaign-view-btn"
                          onClick={() => setSelectedCampaign(campaign)}
                        >
                          View Campaign
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {!campaignsLoading && !campaignsError && activeCampaigns.length === 0 && (
                  <div className="empty-state">
                    <div>🔎</div>
                    <h3>No campaigns found</h3>
                    <p>Try matching another title, category, or search term.</p>
                  </div>
                )}
              </section>
            )}

            {donorSection === "donations" && (
              <section className="donor-section-page">
                <div className="donor-page-heading">
                  <div>
                    <span className="section-kicker">DONATION HISTORY</span>
                    <h1>My Donations</h1>
                    <p>Track your contributions and successful payments.</p>
                  </div>
                </div>

                <div className="donation-summary-grid">
                  <div className="summary-mini-card">
                    <span>Total Donated</span>
                    <strong>{formatCurrency(totalDonatedAmount)}</strong>
                  </div>
                  <div className="summary-mini-card">
                    <span>Successful Donations</span>
                    <strong>{myDonations.length}</strong>
                  </div>
                  <div className="summary-mini-card">
                    <span>Campaigns Supported</span>
                    <strong>{uniqueCampaignsSupported}</strong>
                  </div>
                </div>

                <div className="full-donation-table">
                  <div className="donation-table-header">
                    <span>Campaign ID</span>
                    <span>Donation ID</span>
                    <span>Amount</span>
                    <span>Status</span>
                  </div>

                  {myDonations.length === 0 ? (
                    <div className="empty-state">
                      <div>💰</div>
                      <h3>No donations record found</h3>
                      <p>When you donate to campaigns, your records will appear here.</p>
                    </div>
                  ) : (
                    myDonations.map((donation) => (
                      <div className="donation-table-row" key={donation.donation_id}>
                        <strong>Campaign #{donation.campaign_id}</strong>
                        <span>DON-{donation.donation_id}</span>
                        <strong>{formatCurrency(donation.amount)}</strong>
                        <span className="status-pill">Successful</span>
                      </div>
                    ))
                  )}
                </div>
              </section>
            )}

            {donorSection === "saved" && (
              <section className="donor-section-page">
                <div className="donor-page-heading">
                  <div>
                    <span className="section-kicker">YOUR SHORTLIST</span>
                    <h1>Saved Campaigns</h1>
                    <p>Keep campaigns here when you want to support them later.</p>
                  </div>
                  <button className="text-action-btn" onClick={fetchSavedCampaigns}>
                    ↻ Refresh
                  </button>
                </div>

                {savedCampaignsLoading && (
                  <div className="empty-state">
                    <div>⏳</div>
                    <h3>Loading saved campaigns...</h3>
                  </div>
                )}

                {!savedCampaignsLoading && savedCampaignsError && (
                  <div className="empty-state">
                    <div>⚠️</div>
                    <h3>Unable to load saved campaigns</h3>
                    <p style={{ color: "#dc2626", fontWeight: "600" }}>{savedCampaignsError}</p>
                    <button className="primary-action-btn" onClick={fetchSavedCampaigns}>
                      Try Again
                    </button>
                  </div>
                )}

                {!savedCampaignsLoading && !savedCampaignsError && savedCampaignsData.length === 0 && (
                  <div className="empty-state">
                    <div>♡</div>
                    <h3>No saved campaigns yet</h3>
                    <p>Save campaigns from Explore Campaigns to find them here.</p>
                    <button className="primary-action-btn" onClick={() => setDonorSection("campaigns")}>
                      Explore Campaigns
                    </button>
                  </div>
                )}

                {!savedCampaignsLoading && !savedCampaignsError && savedCampaignsData.length > 0 && (
                  <div className="campaign-card-grid">
                    {savedCampaignsData.map((item) => {
                      const camp = item.campaign;
                      if (!camp) return null;
                      const campaign = {
                        id: camp.campaign_id,
                        title: camp.title,
                        category: camp.category,
                        description: camp.description,
                        raised: Number(camp.collected_amount || 0),
                        goal: Number(camp.goal_amount || 0),
                        status: camp.status,
                        icon: getCampaignIcon(camp.category),
                        creator_id: camp.creator_id,
                        start_date: camp.start_date,
                        end_date: camp.end_date,
                      };
                      return (
                        <div className="campaign-card" key={camp.campaign_id}>
                          <div className="campaign-card-top">
                            <div className="campaign-icon">{campaign.icon}</div>
                            <button
                              className={savingCampaignId === camp.campaign_id ? "save-btn saving" : "save-btn saved"}
                              onClick={() => toggleSavedCampaign(camp.campaign_id)}
                              disabled={savingCampaignId === camp.campaign_id}
                            >
                              {savingCampaignId === camp.campaign_id ? "⏳" : "♥"}
                            </button>
                          </div>

                          <span className="campaign-category">{campaign.category}</span>
                          <h3>{campaign.title}</h3>
                          <p>{campaign.description}</p>

                          <div className="campaign-amount-row">
                            <strong>{formatCurrency(campaign.raised)}</strong>
                            <span>of {formatCurrency(campaign.goal)}</span>
                          </div>

                          <div className="progress-track">
                            <div
                              className="progress-fill"
                              style={{
                                width: `${progressPercentage(campaign.raised, campaign.goal)}%`,
                              }}
                            ></div>
                          </div>

                          <div className="campaign-meta-row">
                            <span>{progressPercentage(campaign.raised, campaign.goal)}% funded</span>
                            <span>{campaign.status}</span>
                          </div>

                          <button
                            className="campaign-view-btn"
                            onClick={() => setSelectedCampaign(campaign)}
                          >
                            View Campaign
                          </button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </section>
            )}

            {donorSection === "notifications" && (
              <section className="donor-section-page">
                <div className="donor-page-heading">
                  <div>
                    <span className="section-kicker">UPDATES</span>
                    <h1>Notifications</h1>
                    <p>Stay updated about your donations and saved campaigns.</p>
                  </div>
                  {unreadCount > 0 && (
                    <button className="admin-tab-btn" onClick={handleMarkAllRead}>
                      Mark all as read
                    </button>
                  )}
                </div>

                {notificationsLoading && (
                  <div className="empty-state">
                    <div>⏳</div>
                    <h3>Loading notifications...</h3>
                  </div>
                )}

                {!notificationsLoading && notificationsError && (
                  <div className="empty-state">
                    <div>⚠️</div>
                    <h3>Unable to load notifications</h3>
                    <p style={{ color: "#dc2626", fontWeight: "600" }}>{notificationsError}</p>
                    <button className="primary-action-btn" onClick={fetchNotifications}>
                      Try Again
                    </button>
                  </div>
                )}

                {!notificationsLoading && !notificationsError && notifications.length === 0 && (
                  <div className="empty-state">
                    <div>🔔</div>
                    <h3>You're all caught up!</h3>
                    <p>Important account updates and campaign alerts will show here.</p>
                  </div>
                )}

                {!notificationsLoading && !notificationsError && notifications.length > 0 && (
                  <div className="notification-list">
                    {notifications.map((notif) => (
                      <div
                        className={`notification-card ${notif.is_read ? "" : "notification-unread"}`}
                        key={notif.notification_id}
                      >
                        <div className="notification-icon">🔔</div>
                        <div className="notification-content">
                          <strong>{notif.title}</strong>
                          <p>{notif.message}</p>
                          <span className="notification-meta">
                            {formatRelativeTime(notif.created_at)}
                            {notif.notification_type && ` • ${notif.notification_type}`}
                          </span>
                        </div>
                        <div className="notification-actions">
                          {!notif.is_read && <span className="notification-dot"></span>}
                          {!notif.is_read && (
                            <button
                              className="text-action-btn"
                              onClick={() => handleMarkRead(notif.notification_id)}
                            >
                              Mark as read
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            )}

            {donorSection === "profile" && (
              <section className="donor-section-page">
                <div className="donor-page-heading">
                  <div>
                    <span className="section-kicker">ACCOUNT</span>
                    <h1>My Profile</h1>
                    <p>View your FundAI donor account information.</p>
                  </div>
                </div>

                <div className="profile-layout">
                  <div className="profile-card">
                    <div className="profile-avatar">
                      {(user?.name || "D").charAt(0).toUpperCase()}
                    </div>
                    <h2>{user?.name}</h2>
                    <span className="profile-role">DONOR</span>
                    <p>Thank you for being part of the FundAI community.</p>
                  </div>

                  <div className="profile-details-card">
                    <div className="profile-detail">
                      <span>Full Name</span>
                      <strong>{user?.name || "Not available"}</strong>
                    </div>
                    <div className="profile-detail">
                      <span>Email Address</span>
                      <strong>{user?.email || "Not available"}</strong>
                    </div>
                    <div className="profile-detail">
                      <span>Account Type</span>
                      <strong>Donor</strong>
                    </div>
                    <div className="profile-detail">
                      <span>User ID</span>
                      <strong>{user?.user_id || "Not available"}</strong>
                    </div>
                  </div>
                </div>
              </section>
            )}
          </main>
        </div>

        {message && (
          <div className={`dashboard-toast ${messageType === "error" ? "toast-error" : "toast-success"}`}>
            {message}
          </div>
        )}

        {/* CAMPAIGN DETAILS MODAL */}
        {selectedCampaign && (
          <div className="modal-overlay" onClick={() => setSelectedCampaign(null)}>
            <div className="modal-card" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>{selectedCampaign.title}</h2>
                <button className="modal-close-btn" onClick={() => setSelectedCampaign(null)}>×</button>
              </div>

              <span className="campaign-category">{selectedCampaign.category}</span>
              <p style={{ margin: "16px 0", color: "#475569", lineHeight: "1.6" }}>
                {selectedCampaign.description}
              </p>

              <div className="campaign-amount-row" style={{ margin: "16px 0 8px" }}>
                <strong style={{ fontSize: "1.2rem", color: "#16a34a" }}>
                  {formatCurrency(selectedCampaign.raised)}
                </strong>
                <span>raised of {formatCurrency(selectedCampaign.goal)}</span>
              </div>

              <div className="progress-track" style={{ height: "10px", marginBottom: "16px" }}>
                <div
                  className="progress-fill"
                  style={{ width: `${progressPercentage(selectedCampaign.raised, selectedCampaign.goal)}%` }}
                ></div>
              </div>

              <div className="profile-details-card" style={{ gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "20px" }}>
                <div className="profile-detail">
                  <span>Status</span>
                  <span className={`badge badge-${selectedCampaign.status.toLowerCase()}`}>
                    {selectedCampaign.status}
                  </span>
                </div>
                <div className="profile-detail">
                  <span>Remaining</span>
                  <strong>{formatCurrency(Math.max(0, selectedCampaign.goal - selectedCampaign.raised))}</strong>
                </div>
              </div>

              <div style={{ display: "flex", gap: "12px" }}>
                <button
                  className="primary-action-btn"
                  style={{ flex: 1 }}
                  onClick={() => {
                    setDonationModalOpen(true);
                  }}
                >
                  Donate Now 💰
                </button>
                <button
                  className={savedCampaignIds.includes(selectedCampaign.id) ? "save-btn saved" : "save-btn"}
                  onClick={() => toggleSavedCampaign(selectedCampaign.id)}
                  style={{ width: "auto", padding: "0 14px" }}
                  disabled={savingCampaignId === selectedCampaign.id}
                >
                  {savingCampaignId === selectedCampaign.id ? "⏳" : (savedCampaignIds.includes(selectedCampaign.id) ? "Saved" : "Save")}
                </button>
                <button
                  className="main-btn"
                  style={{ width: "auto", background: "#f1f5f9", color: "#334155" }}
                  onClick={() => setSelectedCampaign(null)}
                >
                  Close
                </button>
              </div>

              {/* COMMENTS SECTION */}
              <div className="comment-section" style={{ marginTop: "24px" }}>
                <h3 style={{ marginBottom: "12px", color: "#17201a" }}>Comments</h3>

                {commentsLoading ? (
                  <div className="empty-state">
                    <div>⏳</div>
                    <h3>Loading comments...</h3>
                  </div>
                ) : commentsError ? (
                  <div className="empty-state">
                    <div>⚠️</div>
                    <h3>Unable to load comments</h3>
                    <p style={{ color: "#dc2626", fontWeight: "600" }}>{commentsError}</p>
                  </div>
                ) : comments.length === 0 ? (
                  <div className="empty-state" style={{ padding: "24px" }}>
                    <div>💬</div>
                    <h3>No comments yet</h3>
                    <p>Be the first to comment on this campaign!</p>
                  </div>
                ) : (
                  <div className="comment-list">
                    {comments.map((comment) => (
                      <div className="comment-card" key={comment.comment_id}>
                        <div className="comment-avatar">
                          {(comment.user_name || "U").charAt(0).toUpperCase()}
                        </div>
                        <div className="comment-body">
                          <div className="comment-header">
                            <strong>{comment.user_name}</strong>
                            <span>{formatRelativeTime(comment.created_at)}</span>
                            {comment.updated_at && <span className="comment-edited">(edited)</span>}
                          </div>
                          {editingCommentId === comment.comment_id ? (
                            <div className="comment-edit-form">
                              <textarea
                                value={editCommentText}
                                onChange={(e) => setEditCommentText(e.target.value)}
                                rows="3"
                                style={{ width: "100%", padding: "8px", borderRadius: "8px", border: "1px solid #e2eee6", resize: "vertical" }}
                              />
                              <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
                                <button className="primary-action-btn" style={{ padding: "6px 14px" }} onClick={() => handleUpdateComment(comment.comment_id)}>
                                  Save
                                </button>
                                <button
                                  className="main-btn"
                                  style={{ background: "#f1f5f9", color: "#334155", padding: "6px 14px" }}
                                  onClick={() => { setEditingCommentId(null); setEditCommentText(""); }}
                                >
                                  Cancel
                                </button>
                              </div>
                            </div>
                          ) : (
                            <p className="comment-text">{comment.comment_text}</p>
                          )}
                          {comment.user_id === user?.user_id && (
                            <div className="comment-actions">
                              <button className="text-action-btn" onClick={() => { setEditingCommentId(comment.comment_id); setEditCommentText(comment.comment_text); }}>
                                Edit
                              </button>
                              <button className="text-action-btn" style={{ color: "#dc2626" }} onClick={() => handleDeleteComment(comment.comment_id)}>
                                Delete
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* COMMENT FORM */}
                <form onSubmit={handlePostComment} className="comment-form">
                  <textarea
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                    placeholder="Write a comment..."
                    rows="3"
                    style={{ width: "100%", padding: "10px", borderRadius: "8px", border: "1px solid #e2eee6", resize: "vertical" }}
                  />
                  <button type="submit" className="primary-action-btn" style={{ marginTop: "8px" }} disabled={postingComment}>
                    {postingComment ? "Posting..." : "Post Comment"}
                  </button>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* DONATION MODAL */}
        {donationModalOpen && selectedCampaign && (
          <div className="modal-overlay" onClick={() => setDonationModalOpen(false)}>
            <div className="modal-card" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Make a Donation</h2>
                <button className="modal-close-btn" onClick={() => setDonationModalOpen(false)}>×</button>
              </div>

              <p style={{ marginBottom: "16px", color: "#475569" }}>
                Supporting: <strong>{selectedCampaign.title}</strong>
              </p>

              <form onSubmit={handleDonateSubmit}>
                <div className="input-group">
                  <label>Donation Amount (₹)</label>
                  <input
                    type="number"
                    min="1"
                    step="100"
                    placeholder="e.g. 1000"
                    value={donationAmount}
                    onChange={(e) => setDonationAmount(e.target.value)}
                    required
                  />
                </div>

                <div style={{ display: "flex", gap: "10px", margin: "16px 0" }}>
                  {[500, 1000, 2000, 5000].map((amt) => (
                    <button
                      key={amt}
                      type="button"
                      className="admin-tab-btn"
                      style={{ padding: "6px 12px", fontSize: "0.85rem" }}
                      onClick={() => setDonationAmount(amt.toString())}
                    >
                      +₹{amt}
                    </button>
                  ))}
                </div>

                <button type="submit" className="main-btn" disabled={donating}>
                  {donating ? "Processing Mock Payment..." : `Confirm Payment of ${formatCurrency(Number(donationAmount || 0))}`}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    );
  }

  /* ================================
     CAMPAIGNER PAGE
  ================================= */

  if (page === "campaigner") {
    if (user?.role !== "CAMPAIGNER" && user?.role !== "ADMIN") {
      return (
        <div className="auth-page">
          <div className="auth-wrapper" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "40px", textAlign: "center" }}>
            <h2>Access Denied 🔒</h2>
            <p style={{ margin: "16px 0", color: "#64748b" }}>You do not have permissions to access the Campaigner Dashboard.</p>
            <button className="primary-action-btn" onClick={() => setPage(user?.role === "DONOR" ? "donor" : "login")}>
              Return to Dashboard
            </button>
          </div>
        </div>
      );
    }

    const myCampaigns = donorCampaigns.filter(
      (campaign) => Number(campaign.creator_id) === Number(user?.user_id || 0)
    );

    const activeCount = myCampaigns.filter((c) => c.status === "ACTIVE").length;
    const pendingCount = myCampaigns.filter((c) => c.status === "PENDING").length;
    const totalRaised = myCampaigns.reduce((acc, c) => acc + (c.raised || 0), 0);

    return (
      <div className="dashboard-page">
        <nav className="dashboard-nav">
          <div className="dashboard-logo">
            <div>F</div>
            <span>FundAI Campaigner</span>
          </div>

          <div className="dashboard-user">
            <span>{user?.name}</span>
            <button onClick={handleLogout}>Logout</button>
          </div>
        </nav>

        <main className="dashboard-content">
          <div className="welcome-card">
            <div>
              <span className="welcome-label">CAMPAIGNER CONTROL PANEL</span>
              <h1>Welcome back, {user?.name} 👋</h1>
              <p>Manage your fundraising campaigns, track progress, and view received contributions.</p>
            </div>
          </div>

          {message && (
            <div className={`alert ${messageType === "error" ? "alert-error" : "alert-success"}`}>
              {message}
            </div>
          )}

          <div className="admin-tabs" style={{ marginTop: "16px" }}>
            <button
              className={`admin-tab-btn ${campaignerTab === "overview" ? "active" : ""}`}
              onClick={() => setCampaignerTab("overview")}
            >
              📊 Overview & Statistics
            </button>
            <button
              className={`admin-tab-btn ${campaignerTab === "create" ? "active" : ""}`}
              onClick={() => setCampaignerTab("create")}
            >
              ➕ Create Campaign
            </button>
            <button
              className={`admin-tab-btn ${campaignerTab === "my-campaigns" ? "active" : ""}`}
              onClick={() => setCampaignerTab("my-campaigns")}
            >
              🚀 My Campaigns ({myCampaigns.length})
            </button>
            <button
              className={`admin-tab-btn ${campaignerTab === "donations" ? "active" : ""}`}
              onClick={() => setCampaignerTab("donations")}
            >
              💰 Donations Received ({receivedDonations.length})
            </button>
            <button
              className={`admin-tab-btn ${campaignerTab === "notifications" ? "active" : ""}`}
              onClick={() => setCampaignerTab("notifications")}
            >
              🔔 Notifications {unreadCount > 0 && `(${unreadCount})`}
            </button>
          </div>

          {campaignerTab === "overview" && (
            <section className="donor-stat-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
              <div className="donor-stat-card">
                <div className="stat-icon">📋</div>
                <div>
                  <span>Total Campaigns</span>
                  <strong>{myCampaigns.length}</strong>
                  <small>Submitted by you</small>
                </div>
              </div>

              <div className="donor-stat-card">
                <div className="stat-icon">✅</div>
                <div>
                  <span>Active Campaigns</span>
                  <strong>{activeCount}</strong>
                  <small>Approved & accepting donations</small>
                </div>
              </div>

              <div className="donor-stat-card">
                <div className="stat-icon">⏳</div>
                <div>
                  <span>Pending Review</span>
                  <strong>{pendingCount}</strong>
                  <small>Awaiting admin approval</small>
                </div>
              </div>

              <div className="donor-stat-card">
                <div className="stat-icon">🌱</div>
                <div>
                  <span>Total Amount Raised</span>
                  <strong>{formatCurrency(totalRaised)}</strong>
                  <small>Across all your campaigns</small>
                </div>
              </div>

              <div className="donor-stat-card">
                <div className="stat-icon">💰</div>
                <div>
                  <span>Donations Received</span>
                  <strong>{receivedDonations.length}</strong>
                  <small>Direct contributions</small>
                </div>
              </div>

              <div className="donor-stat-card">
                <div className="stat-icon">🔔</div>
                <div>
                  <span>Unread Notifications</span>
                  <strong>{unreadCount}</strong>
                  <small>Waiting for your attention</small>
                </div>
              </div>
            </section>
          )}

          {campaignerTab === "create" && (
            <div className="create-campaign-wrapper">
              <div className="create-campaign-card">
                <div className="create-campaign-header">
                  <div className="header-icon-box">🚀</div>
                  <div className="header-text">
                    <div className="header-badge">Step 1 of 1 • Campaign Setup</div>
                    <h2>Launch a New Campaign</h2>
                    <p>Fill in details to submit your campaign. It will be reviewed by an admin before going LIVE.</p>
                  </div>
                </div>

                <form onSubmit={handleCreateCampaign} className="create-campaign-form">
                  {/* SECTION 1: CAMPAIGN FUNDAMENTALS */}
                  <div className="form-section">
                    <h4 className="form-section-title">
                      <span>📝</span> 1. Basic Campaign Information
                    </h4>

                    <div className="form-group">
                      <label htmlFor="campaign-title">Campaign Title <span className="req">*</span></label>
                      <div className="input-with-icon">
                        <span className="field-icon">🎯</span>
                        <input
                          id="campaign-title"
                          type="text"
                          className="form-input"
                          value={campaignForm.title}
                          onChange={(e) => setCampaignForm({ ...campaignForm, title: e.target.value })}
                          placeholder="e.g. Village School Supplies & Library Drive"
                          required
                        />
                      </div>
                    </div>

                    <div className="form-grid-2">
                      <div className="form-group">
                        <label htmlFor="campaign-category">Category <span className="req">*</span></label>
                        <div className="input-with-icon">
                          <span className="field-icon">🏷️</span>
                          <select
                            id="campaign-category"
                            className="form-select"
                            value={campaignForm.category}
                            onChange={(e) => setCampaignForm({ ...campaignForm, category: e.target.value })}
                            required
                          >
                            <option value="Education">🎓 Education</option>
                            <option value="Medical">🏥 Medical</option>
                            <option value="Food">🍲 Food & Hunger Relief</option>
                            <option value="Emergency">🚨 Emergency Relief</option>
                            <option value="Community">🏘️ Community Development</option>
                            <option value="Children">👶 Children & Youth</option>
                          </select>
                        </div>
                      </div>

                      <div className="form-group">
                        <label htmlFor="campaign-goal">Goal Amount (₹) <span className="req">*</span></label>
                        <div className="input-with-prefix">
                          <span className="prefix-badge">₹</span>
                          <input
                            id="campaign-goal"
                            type="number"
                            min="1"
                            step="100"
                            className="form-input prefix-padding"
                            value={campaignForm.goal_amount}
                            onChange={(e) => setCampaignForm({ ...campaignForm, goal_amount: e.target.value })}
                            placeholder="100000"
                            required
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* SECTION 2: TIMELINE & MEDIA */}
                  <div className="form-section">
                    <h4 className="form-section-title">
                      <span>📅</span> 2. Timeline & Banner Image
                    </h4>

                    <div className="form-grid-2">
                      <div className="form-group">
                        <label htmlFor="campaign-start">Start Date <span className="opt">(Optional)</span></label>
                        <input
                          id="campaign-start"
                          type="date"
                          className="form-input"
                          value={campaignForm.start_date}
                          onChange={(e) => setCampaignForm({ ...campaignForm, start_date: e.target.value })}
                        />
                      </div>

                      <div className="form-group">
                        <label htmlFor="campaign-end">End Date <span className="opt">(Optional)</span></label>
                        <input
                          id="campaign-end"
                          type="date"
                          className="form-input"
                          value={campaignForm.end_date}
                          onChange={(e) => setCampaignForm({ ...campaignForm, end_date: e.target.value })}
                        />
                      </div>
                    </div>

                    <div className="form-group">
                      <label htmlFor="campaign-image">Banner Image URL <span className="opt">(Optional)</span></label>
                      <div className="input-with-icon">
                        <span className="field-icon">🖼️</span>
                        <input
                          id="campaign-image"
                          type="url"
                          className="form-input"
                          value={campaignForm.image_url}
                          onChange={(e) => setCampaignForm({ ...campaignForm, image_url: e.target.value })}
                          placeholder="https://example.com/banner.jpg"
                        />
                      </div>
                      {campaignForm.image_url && (
                        <div className="image-preview-container">
                          <span className="preview-label">Image Preview:</span>
                          <img
                            src={campaignForm.image_url}
                            alt="Banner preview"
                            onError={(e) => { e.target.style.display = 'none'; }}
                          />
                        </div>
                      )}
                    </div>
                  </div>

                  {/* SECTION 3: DETAILED DESCRIPTION */}
                  <div className="form-section">
                    <h4 className="form-section-title">
                      <span>📖</span> 3. Campaign Story & Description
                    </h4>

                    <div className="form-group">
                      <label htmlFor="campaign-desc">Detailed Description <span className="req">*</span></label>
                      <textarea
                        id="campaign-desc"
                        rows="6"
                        className="form-textarea"
                        value={campaignForm.description}
                        onChange={(e) => setCampaignForm({ ...campaignForm, description: e.target.value })}
                        placeholder="Describe the cause in detail: who benefits, how funds will be utilized, and why donors should support this cause."
                        required
                      />
                      <small className="field-hint">Tip: Clear and transparent descriptions attract 3x more donations!</small>
                    </div>
                  </div>

                  {campaignFormError && (
                    <div className="alert alert-error" style={{ marginBottom: "20px" }}>
                      <span>⚠️</span> {campaignFormError}
                    </div>
                  )}

                  <div className="form-action-bar">
                    <button type="submit" className="create-campaign-submit-btn" disabled={campaignFormLoading}>
                      {campaignFormLoading ? (
                        <>
                          <span className="btn-spinner"></span> Submitting for Review...
                        </>
                      ) : (
                        <>
                          <span>🚀</span> Submit Campaign for Approval
                        </>
                      )}
                    </button>
                    <p className="form-security-notice">
                      🛡️ Your campaign will be sent to the FundAI Admin team for approval before going LIVE.
                    </p>
                  </div>
                </form>
              </div>
            </div>
          )}

          {campaignerTab === "my-campaigns" && (
            <div>
              {campaignsLoading ? (
                <p>Loading your campaigns...</p>
              ) : myCampaigns.length === 0 ? (
                <div className="empty-state">
                  <div>🚀</div>
                  <h3>No campaigns created yet</h3>
                  <p>Click "Create Campaign" to submit your first fundraising project!</p>
                  <button className="primary-action-btn" onClick={() => setCampaignerTab("create")}>
                    Create Campaign Now
                  </button>
                </div>
              ) : (
                <div className="campaign-card-grid large">
                  {myCampaigns.map((campaign) => (
                    <div className="campaign-card" key={campaign.id}>
                      <div className="campaign-card-top">
                        <div className="campaign-icon">{campaign.icon}</div>
                        <span className={`badge badge-${campaign.status.toLowerCase()}`}>{campaign.status}</span>
                      </div>

                      <span className="campaign-category">{campaign.category}</span>
                      <h3>{campaign.title}</h3>
                      <p>{campaign.description}</p>

                      <div className="campaign-amount-row">
                        <strong>{formatCurrency(campaign.raised)}</strong>
                        <span>of {formatCurrency(campaign.goal)}</span>
                      </div>

                      <div className="progress-track">
                        <div
                          className="progress-fill"
                          style={{ width: `${progressPercentage(campaign.raised, campaign.goal)}%` }}
                        ></div>
                      </div>

                      <div className="campaign-meta-row">
                        <span>{progressPercentage(campaign.raised, campaign.goal)}% funded</span>
                        <span>ID #{campaign.id}</span>
                      </div>

                      <div style={{ display: "flex", gap: "8px", marginTop: "16px" }}>
                        <button
                          className="campaign-view-btn"
                          style={{ flex: 1 }}
                          onClick={() => setSelectedCampaign(campaign)}
                        >
                          View
                        </button>
                        <button
                          className="admin-tab-btn"
                          style={{ padding: "8px 14px", fontSize: "0.85rem" }}
                          onClick={() => handleOpenEdit(campaign)}
                        >
                          Edit ✏️
                        </button>
                        <button
                          className="btn-reject"
                          style={{ padding: "8px 14px", fontSize: "0.85rem" }}
                          onClick={() => handleDeleteCampaign(campaign.id, campaign.title)}
                        >
                          Delete 🗑️
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {campaignerTab === "donations" && (
            <div className="admin-table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Donation ID</th>
                    <th>Campaign ID</th>
                    <th>Donor ID</th>
                    <th>Amount</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {receivedDonations.length === 0 ? (
                    <tr>
                      <td colSpan="5" style={{ textAlign: "center", padding: "24px", color: "#64748b" }}>
                        No donations received yet for your campaigns.
                      </td>
                    </tr>
                  ) : (
                    receivedDonations.map((d) => (
                      <tr key={d.donation_id}>
                        <td>#DON-{d.donation_id}</td>
                        <td>Campaign #{d.campaign_id}</td>
                        <td>Donor #{d.donor_id}</td>
                        <td><strong>{formatCurrency(d.amount)}</strong></td>
                        <td><span className="badge badge-active">{d.status || d.payment_status || "SUCCESS"}</span></td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {campaignerTab === "notifications" && (
            <div className="donor-section-page">
              <div className="donor-page-heading">
                <div>
                  <span className="section-kicker">UPDATES</span>
                  <h1>Notifications</h1>
                  <p>Stay updated about your campaigns and donations.</p>
                </div>
                {unreadCount > 0 && (
                  <button className="admin-tab-btn" onClick={handleMarkAllRead}>
                    Mark all as read
                  </button>
                )}
              </div>

              {notificationsLoading ? (
                <div className="empty-state">
                  <div>⏳</div>
                  <h3>Loading notifications...</h3>
                </div>
              ) : notificationsError ? (
                <div className="empty-state">
                  <div>⚠️</div>
                  <h3>Unable to load notifications</h3>
                  <p style={{ color: "#dc2626", fontWeight: "600" }}>{notificationsError}</p>
                  <button className="primary-action-btn" onClick={fetchNotifications}>
                    Try Again
                  </button>
                </div>
              ) : notifications.length === 0 ? (
                <div className="empty-state">
                  <div>🔔</div>
                  <h3>You're all caught up!</h3>
                  <p>Important account updates and campaign alerts will show here.</p>
                </div>
              ) : (
                <div className="notification-list">
                  {notifications.map((notif) => (
                    <div
                      className={`notification-card ${notif.is_read ? "" : "notification-unread"}`}
                      key={notif.notification_id}
                    >
                      <div className="notification-icon">🔔</div>
                      <div className="notification-content">
                        <strong>{notif.title}</strong>
                        <p>{notif.message}</p>
                        <span className="notification-meta">
                          {formatRelativeTime(notif.created_at)}
                          {notif.notification_type && ` • ${notif.notification_type}`}
                        </span>
                      </div>
                      <div className="notification-actions">
                        {!notif.is_read && <span className="notification-dot"></span>}
                        {!notif.is_read && (
                          <button
                            className="text-action-btn"
                            onClick={() => handleMarkRead(notif.notification_id)}
                          >
                            Mark as read
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </main>

        {editingCampaign && (
          <div className="modal-overlay" onClick={() => setEditingCampaign(null)}>
            <div className="modal-card" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Edit Campaign</h2>
                <button className="modal-close-btn" onClick={() => setEditingCampaign(null)}>×</button>
              </div>

              <form onSubmit={handleUpdateCampaign}>
                <div className="input-group">
                  <label>Title</label>
                  <input
                    type="text"
                    value={editForm.title}
                    onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                    required
                  />
                </div>

                <div className="input-group">
                  <label>Category</label>
                  <select
                    value={editForm.category}
                    onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                    required
                  >
                    <option value="Education">Education</option>
                    <option value="Medical">Medical</option>
                    <option value="Food">Food</option>
                    <option value="Emergency">Emergency</option>
                    <option value="Community">Community</option>
                    <option value="Children">Children</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Goal Amount (₹)</label>
                  <input
                    type="number"
                    min="1"
                    value={editForm.goal_amount}
                    onChange={(e) => setEditForm({ ...editForm, goal_amount: e.target.value })}
                    required
                  />
                </div>

                <div className="input-group">
                  <label>Description</label>
                  <textarea
                    rows="4"
                    value={editForm.description}
                    onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                    required
                  />
                </div>

                <div style={{ display: "flex", gap: "12px", marginTop: "16px" }}>
                  <button type="submit" className="main-btn" disabled={editLoading}>
                    {editLoading ? "Saving..." : "Save Changes"}
                  </button>
                  <button
                    type="button"
                    className="main-btn"
                    style={{ background: "#f1f5f9", color: "#334155" }}
                    onClick={() => setEditingCampaign(null)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    );
  }

  /* ================================
     ADMIN PAGE
  ================================= */

  if (page === "admin") {
    const pendingCampaignsList = adminCampaigns.filter((c) => c.status === "PENDING");

    const filteredUsers = adminUsers.filter((u) => {
      const matchesSearch =
        u.name.toLowerCase().includes(adminUserSearch.toLowerCase()) ||
        u.email.toLowerCase().includes(adminUserSearch.toLowerCase()) ||
        String(u.user_id).includes(adminUserSearch);
      const matchesRole = adminUserRoleFilter === "ALL" || u.role === adminUserRoleFilter;
      const matchesStatus =
        adminUserStatusFilter === "ALL" ||
        (adminUserStatusFilter === "ACTIVE" && u.is_active !== false) ||
        (adminUserStatusFilter === "INACTIVE" && u.is_active === false);
      return matchesSearch && matchesRole && matchesStatus;
    });

    const filteredCampaigns = adminCampaigns.filter((c) => {
      const matchesSearch =
        c.title.toLowerCase().includes(adminCampaignSearch.toLowerCase()) ||
        String(c.campaign_id).includes(adminCampaignSearch);
      const matchesStatus = adminCampaignStatusFilter === "ALL" || c.status === adminCampaignStatusFilter;
      return matchesSearch && matchesStatus;
    });

    const adminNavItems = [
      { id: "overview", icon: "📊", label: "Overview" },
      { id: "users", icon: "👥", label: `Users (${adminUsers.length})` },
      { id: "campaigns", icon: "🚀", label: `Campaigns (${adminCampaigns.length})` },
      { id: "approvals", icon: "📋", label: "Pending Approvals", badge: pendingCampaignsList.length },
      { id: "donations", icon: "💰", label: `Donations (${adminDonations.length})` },
      { id: "transactions", icon: "💳", label: `Transactions (${adminTransactions.length})` },
      { id: "reports", icon: "📈", label: "Reports & Analytics" },
      { id: "audit_logs", icon: "🛡️", label: "Audit Logs" },
      { id: "notifications", icon: "🔔", label: "Notifications", badge: unreadCount },
      { id: "profile", icon: "👤", label: "Admin Profile" },
    ];

    return (
      <div className="dashboard-page admin-dashboard-page">
        {/* TOP BRAND & USER BAR */}
        <header className="admin-top-bar">
          <div className="admin-brand-logo">
            <div className="admin-logo-icon">F</div>
            <div className="admin-logo-text">
              <span className="brand-title">FundAI Admin</span>
              <span className="brand-badge">Control Center</span>
            </div>
          </div>

          <div className="admin-user-profile">
            <div className="admin-avatar">🛡️</div>
            <div className="admin-user-info">
              <span className="user-name">{user?.name || "System Admin"}</span>
              <span className="user-role">Administrator</span>
            </div>
            <button className="admin-logout-btn" onClick={handleLogout}>
              <span>🚪</span> Logout
            </button>
          </div>
        </header>

        {/* ENHANCED GREEN PILL NAVIGATION BAR */}
        <nav className="admin-nav-bar">
          <div className="admin-nav-container">
            {adminNavItems.map((item) => (
              <button
                key={item.id}
                className={`admin-nav-pill ${adminTab === item.id ? "active" : ""}`}
                onClick={() => setAdminTab(item.id)}
              >
                <span className="pill-icon">{item.icon}</span>
                <span className="pill-label">{item.label}</span>
                {item.badge > 0 && <span className="pill-badge">{item.badge}</span>}
              </button>
            ))}
          </div>
        </nav>

        <main className="dashboard-content">
          <div className="welcome-card">
            <div>
              <span className="welcome-label">ADMINISTRATION & PLATFORM CONTROL</span>
              <h1>Platform Control Center 🛡️</h1>
              <p>Monitor system activity, manage users, review pending campaigns, and audit actions.</p>
            </div>
          </div>

          {message && (
            <div className={`alert ${messageType === "error" ? "alert-error" : "alert-success"}`}>
              {message}
            </div>
          )}

          {adminLoading && <p style={{ margin: "20px 0" }}>Loading admin data...</p>}

          {/* TAB 1: OVERVIEW */}
          {adminTab === "overview" && adminReports && (
            <>
              <div className="donor-stat-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", marginBottom: "24px" }}>
                <div className="donor-stat-card">
                  <div className="stat-icon">👥</div>
                  <div>
                    <span>Total Users</span>
                    <strong>{adminReports.total_users}</strong>
                  </div>
                </div>
                <div className="donor-stat-card">
                  <div className="stat-icon">🚀</div>
                  <div>
                    <span>Total Campaigns</span>
                    <strong>{adminReports.total_campaigns}</strong>
                  </div>
                </div>
                <div className="donor-stat-card">
                  <div className="stat-icon">⏳</div>
                  <div>
                    <span>Pending Approvals</span>
                    <strong>{adminReports.pending_campaigns}</strong>
                  </div>
                </div>
                <div className="donor-stat-card">
                  <div className="stat-icon">🌱</div>
                  <div>
                    <span>Total Amount Raised</span>
                    <strong>{formatCurrency(adminReports.total_amount_raised)}</strong>
                  </div>
                </div>
                <div className="donor-stat-card">
                  <div className="stat-icon">✅</div>
                  <div>
                    <span>Successful Txns</span>
                    <strong>{adminReports.successful_transactions}</strong>
                  </div>
                </div>
              </div>

              <div className="section-header">
                <h2>Pending Approvals ({pendingCampaignsList.length})</h2>
              </div>
              <div className="admin-table-container">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Title</th>
                      <th>Category</th>
                      <th>Goal Amount</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pendingCampaignsList.length === 0 ? (
                      <tr><td colSpan="6" style={{ textAlign: "center", padding: "20px" }}>No campaigns waiting for approval.</td></tr>
                    ) : (
                      pendingCampaignsList.map((camp) => (
                        <tr key={camp.campaign_id}>
                          <td>#{camp.campaign_id}</td>
                          <td><strong>{camp.title}</strong></td>
                          <td>{camp.category}</td>
                          <td>{formatCurrency(camp.goal_amount)}</td>
                          <td><span className="badge badge-pending">{camp.status}</span></td>
                          <td>
                            <button className="btn-approve" onClick={() => handleAdminApprove(camp.campaign_id)}>Approve</button>
                            <button className="btn-reject" onClick={() => handleAdminReject(camp.campaign_id)}>Reject</button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </>
          )}

          {/* TAB 2: USERS MODULE */}
          {adminTab === "users" && (
            <>
              <div className="donor-filter-bar" style={{ marginBottom: "20px" }}>
                <input
                  type="text"
                  placeholder="Search user by name, email or ID..."
                  value={adminUserSearch}
                  onChange={(e) => setAdminUserSearch(e.target.value)}
                  style={{ flex: 2 }}
                />
                <select value={adminUserRoleFilter} onChange={(e) => setAdminUserRoleFilter(e.target.value)}>
                  <option value="ALL">All Roles</option>
                  <option value="DONOR">Donors Only</option>
                  <option value="CAMPAIGNER">Campaigners Only</option>
                  <option value="ADMIN">Admins Only</option>
                </select>
                <select value={adminUserStatusFilter} onChange={(e) => setAdminUserStatusFilter(e.target.value)}>
                  <option value="ALL">All Statuses</option>
                  <option value="ACTIVE">Active Users</option>
                  <option value="INACTIVE">Deactivated Users</option>
                </select>
              </div>

              <div className="admin-table-container">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>User ID</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.length === 0 ? (
                      <tr><td colSpan="6" style={{ textAlign: "center", padding: "20px" }}>No users match filter.</td></tr>
                    ) : (
                      filteredUsers.map((u) => (
                        <tr key={u.user_id}>
                          <td>#{u.user_id}</td>
                          <td><strong>{u.name}</strong></td>
                          <td>{u.email}</td>
                          <td><span className="badge badge-active">{u.role}</span></td>
                          <td>
                            <span className={`badge ${u.is_active !== false ? "badge-active" : "badge-rejected"}`}>
                              {u.is_active !== false ? "ACTIVE" : "DEACTIVATED"}
                            </span>
                          </td>
                          <td>
                            {u.user_id !== user?.user_id ? (
                              <button
                                className={u.is_active !== false ? "btn-reject" : "btn-approve"}
                                onClick={() => toggleUserActive(u)}
                              >
                                {u.is_active !== false ? "Deactivate" : "Activate"}
                              </button>
                            ) : (
                              <span style={{ color: "#64748b", fontSize: "0.85rem" }}>Your Account</span>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </>
          )}

          {/* TAB 3: CAMPAIGNS MODULE */}
          {adminTab === "campaigns" && (
            <>
              <div className="donor-filter-bar" style={{ marginBottom: "20px" }}>
                <input
                  type="text"
                  placeholder="Search campaigns by title or ID..."
                  value={adminCampaignSearch}
                  onChange={(e) => setAdminCampaignSearch(e.target.value)}
                  style={{ flex: 2 }}
                />
                <select value={adminCampaignStatusFilter} onChange={(e) => setAdminCampaignStatusFilter(e.target.value)}>
                  <option value="ALL">All Statuses</option>
                  <option value="PENDING">Pending</option>
                  <option value="ACTIVE">Active</option>
                  <option value="COMPLETED">Completed</option>
                  <option value="REJECTED">Rejected</option>
                </select>
              </div>

              <div className="admin-table-container">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Title</th>
                      <th>Category</th>
                      <th>Creator ID</th>
                      <th>Goal</th>
                      <th>Collected</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredCampaigns.length === 0 ? (
                      <tr><td colSpan="7" style={{ textAlign: "center", padding: "20px" }}>No campaigns found.</td></tr>
                    ) : (
                      filteredCampaigns.map((camp) => (
                        <tr key={camp.campaign_id}>
                          <td>#{camp.campaign_id}</td>
                          <td><strong>{camp.title}</strong></td>
                          <td>{camp.category}</td>
                          <td>User #{camp.creator_id}</td>
                          <td>{formatCurrency(camp.goal_amount)}</td>
                          <td>{formatCurrency(camp.collected_amount)}</td>
                          <td><span className={`badge badge-${camp.status.toLowerCase()}`}>{camp.status}</span></td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </>
          )}

          {/* TAB 4: PENDING APPROVALS */}
          {adminTab === "approvals" && (
            <div className="admin-table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Creator ID</th>
                    <th>Goal</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {pendingCampaignsList.length === 0 ? (
                    <tr><td colSpan="6" style={{ textAlign: "center", padding: "20px" }}>All campaigns have been reviewed.</td></tr>
                  ) : (
                    pendingCampaignsList.map((camp) => (
                      <tr key={camp.campaign_id}>
                        <td>#{camp.campaign_id}</td>
                        <td><strong>{camp.title}</strong></td>
                        <td>{camp.category}</td>
                        <td>User #{camp.creator_id}</td>
                        <td>{formatCurrency(camp.goal_amount)}</td>
                        <td>
                          <button className="btn-approve" onClick={() => handleAdminApprove(camp.campaign_id)}>Approve</button>
                          <button className="btn-reject" onClick={() => handleAdminReject(camp.campaign_id)}>Reject</button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 5: DONATIONS MODULE */}
          {adminTab === "donations" && (
            <div className="admin-table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Donation ID</th>
                    <th>Donor ID</th>
                    <th>Campaign ID</th>
                    <th>Amount</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {adminDonations.length === 0 ? (
                    <tr><td colSpan="5" style={{ textAlign: "center", padding: "20px" }}>No donations recorded yet.</td></tr>
                  ) : (
                    adminDonations.map((d) => (
                      <tr key={d.donation_id}>
                        <td>#DON-{d.donation_id}</td>
                        <td>User #{d.donor_id}</td>
                        <td>Campaign #{d.campaign_id}</td>
                        <td><strong>{formatCurrency(d.amount)}</strong></td>
                        <td><span className="badge badge-active">{d.status || "SUCCESS"}</span></td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 6: TRANSACTIONS MODULE */}
          {adminTab === "transactions" && (
            <div className="admin-table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Transaction ID</th>
                    <th>Donation ID</th>
                    <th>Payment Reference</th>
                    <th>Amount</th>
                    <th>Gateway</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {adminTransactions.length === 0 ? (
                    <tr><td colSpan="6" style={{ textAlign: "center", padding: "20px" }}>No payment transactions found.</td></tr>
                  ) : (
                    adminTransactions.map((tx) => (
                      <tr key={tx.transaction_id}>
                        <td>#TXN-{tx.transaction_id}</td>
                        <td>#DON-{tx.donation_id}</td>
                        <td><code>{tx.payment_reference}</code></td>
                        <td><strong>{formatCurrency(tx.amount)}</strong></td>
                        <td>{tx.gateway || "mock"}</td>
                        <td><span className={`badge ${tx.status === "SUCCESS" ? "badge-active" : "badge-rejected"}`}>{tx.status}</span></td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 7: REPORTS & ANALYTICS */}
          {adminTab === "reports" && adminReports && (
            <>
              <div className="donor-stat-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", marginBottom: "24px" }}>
                <div className="donor-stat-card">
                  <div className="stat-icon">👥</div>
                  <div>
                    <span>Total Donors</span>
                    <strong>{adminReports.total_donors}</strong>
                  </div>
                </div>
                <div className="donor-stat-card">
                  <div className="stat-icon">📣</div>
                  <div>
                    <span>Total Campaigners</span>
                    <strong>{adminReports.total_campaigners}</strong>
                  </div>
                </div>
                <div className="donor-stat-card">
                  <div className="stat-icon">🎯</div>
                  <div>
                    <span>Completed Campaigns</span>
                    <strong>{adminReports.completed_campaigns}</strong>
                  </div>
                </div>
                <div className="donor-stat-card">
                  <div className="stat-icon">❌</div>
                  <div>
                    <span>Failed Payments</span>
                    <strong>{adminReports.failed_transactions || 0}</strong>
                  </div>
                </div>
              </div>

              <div className="section-header">
                <h2>Campaigns by Category</h2>
              </div>
              <div className="admin-table-container">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Category</th>
                      <th>Campaign Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.keys(adminReports.campaigns_by_category || {}).length === 0 ? (
                      <tr><td colSpan="2" style={{ textAlign: "center", padding: "20px" }}>No category breakdown available.</td></tr>
                    ) : (
                      Object.entries(adminReports.campaigns_by_category || {}).map(([cat, count]) => (
                        <tr key={cat}>
                          <td><strong>{cat}</strong></td>
                          <td>{count} campaigns</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </>
          )}

          {/* TAB 8: AUDIT LOGS */}
          {adminTab === "audit_logs" && (
            <div className="admin-table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Log ID</th>
                    <th>Admin Name</th>
                    <th>Action</th>
                    <th>Target Entity</th>
                    <th>Details</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {adminAuditLogs.length === 0 ? (
                    <tr><td colSpan="6" style={{ textAlign: "center", padding: "20px" }}>No audit log entries recorded yet.</td></tr>
                  ) : (
                    adminAuditLogs.map((log) => (
                      <tr key={log.audit_id}>
                        <td>#LOG-{log.audit_id}</td>
                        <td><strong>{log.admin_name || `Admin #${log.admin_id}`}</strong></td>
                        <td><span className="badge badge-active">{log.action}</span></td>
                        <td>{log.entity_type} #{log.entity_id}</td>
                        <td>{log.details || "—"}</td>
                        <td>{log.created_at ? new Date(log.created_at).toLocaleString() : "—"}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 9: NOTIFICATIONS */}
          {adminTab === "notifications" && (
            <div className="donor-section-content">
              <div className="section-header">
                <h2>Platform System Notifications</h2>
                {unreadCount > 0 && (
                  <button className="text-action-btn" onClick={markAllNotificationsRead}>
                    Mark All as Read
                  </button>
                )}
              </div>
              {notifications.length === 0 ? (
                <p>No notifications.</p>
              ) : (
                notifications.map((n) => (
                  <div key={n.notification_id} className={`notification-item ${!n.is_read ? "unread" : ""}`}>
                    <div>
                      <strong>{n.title}</strong>
                      <p>{n.message}</p>
                      <small>{n.created_at ? new Date(n.created_at).toLocaleString() : ""}</small>
                    </div>
                    {!n.is_read && (
                      <button className="text-action-btn" onClick={() => markNotificationRead(n.notification_id)}>
                        Mark Read
                      </button>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {/* TAB 10: PROFILE */}
          {adminTab === "profile" && (
            <div className="auth-form" style={{ maxWidth: "600px", margin: "0 auto" }}>
              <h2>Admin Profile</h2>
              <div style={{ marginTop: "20px" }}>
                <p><strong>Name:</strong> {user?.name}</p>
                <p><strong>Email:</strong> {user?.email}</p>
                <p><strong>User ID:</strong> #{user?.user_id}</p>
                <p><strong>Role:</strong> <span className="badge badge-active">{user?.role}</span></p>
              </div>
            </div>
          )}
        </main>
      </div>
    );
  }

  // Fallback if page state does not match any route
  useEffect(() => {
    setPage("login");
  }, []);

  return null;
}

export default App;