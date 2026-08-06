# Database Design

## Database Name
Crowdfunding_Fundraising_DB

## Tables

### Users
- user_id (PK)
- full_name
- email
- password
- phone
- role
- created_at

### Campaigns
- campaign_id (PK)
- creator_id (FK)
- category_id (FK)
- title
- description
- target_amount
- raised_amount
- deadline
- status
- created_at

### Categories
- category_id (PK)
- category_name

### Donations
- donation_id (PK)
- campaign_id (FK)
- donor_id (FK)
- amount
- donated_at

### Transactions
- transaction_id (PK)
- donation_id (FK)
- payment_method
- payment_status
- transaction_date

## Relationships

- One User can create many Campaigns.
- One Campaign belongs to one Category.
- One Campaign can receive many Donations.
- One Donation has one Transaction.