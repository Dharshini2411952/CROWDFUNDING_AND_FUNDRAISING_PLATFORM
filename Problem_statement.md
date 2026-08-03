# Problem Statement

## 1. Title

FundBridge – Crowdfunding & Fundraising Platform

---

## 2. Domain

Web Application Development (Crowdfunding & Donation Management)

---

## 3. Who is the user? (2–3 user types, with roles)

### 1. Donor
- Register and login
- Browse fundraising campaigns
- Donate to campaigns
- View donation history
- Track campaign progress

### 2. Campaign Creator (Fundraiser)
- Register and login
- Create fundraising campaigns
- Upload campaign details and images
- Set fundraising goals and deadlines
- View donations received
- Post campaign updates

### 3. Admin
- Verify and approve campaigns
- Manage users
- Monitor donations
- Remove fake or inappropriate campaigns
- Generate reports and analytics

---

## 4. What problem are we solving? (3–5 sentences, real-life example)

Many individuals, students, NGOs, startups, and charitable organizations face difficulties in raising funds because they lack a secure and trustworthy online platform. Existing fundraising platforms may have high service charges or complicated campaign management processes. This project provides a centralized platform where campaign creators can easily raise funds and donors can safely contribute to verified campaigns. For example, a student who requires financial support for higher education can create a fundraising campaign, while donors from different locations can contribute and track the campaign's progress transparently.

---

## 5. Proposed Solution (What the application will do, feature-wise)

The proposed application is a web-based Crowdfunding and Fundraising Platform that allows users to create, manage, and support fundraising campaigns.

Features include:

- User Registration and Login
- Secure Authentication
- Create Fundraising Campaigns
- Upload Campaign Images
- Set Funding Goal and Deadline
- Browse Active Campaigns
- Search and Filter Campaigns
- Online Donation Module
- Campaign Progress Tracking
- Donation History
- Campaign Updates
- User Profile Management
- Admin Dashboard
- Campaign Verification
- Reports and Analytics
- Email Notifications (Future Integration)

---

## 6. Core Entities / Database Tables (Minimum 5)

1. Users
2. Campaigns
3. Donations
4. Categories
5. Campaign_Updates
6. Comments
7. Notifications
8. Admin

---

## 7. User Roles & Permissions

### Admin
- Manage Users
- Verify Campaigns
- Approve or Reject Campaigns
- Delete Fake Campaigns
- View Reports
- Monitor Donations

### Campaign Creator
- Create Campaign
- Edit Campaign
- Delete Campaign
- Upload Images
- View Donations
- Post Updates

### Donor
- Register/Login
- Browse Campaigns
- Donate to Campaigns
- View Donation History
- Update Profile

---

## 8. Success Criteria

The application will be considered successful if:

- Users can successfully register and log in.
- Campaign creators can create and manage fundraising campaigns.
- Donors can browse campaigns and make donations.
- Campaign progress is updated automatically after donations.
- Admin can approve or reject campaigns.
- Users can search and filter campaigns.
- Donation history is maintained correctly.
- All user data is securely stored in the database.

---

## 9. Out of Scope

The following features will NOT be included in Version 1.0:

- Real payment gateway integration (Razorpay/Stripe)
- Mobile Application
- Cryptocurrency Donations
- Live Video Streaming
- AI Fraud Detection
- Multi-language Support
- SMS Notifications
- UPI Integration
- Social Media Login

These features can be implemented in future versions.

---

## 10. Chosen Track

Python (Flask) + React.js + MySQL