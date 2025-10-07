# Admin User Setup Guide

This guide explains how to create and login as an admin user.

## Changes Made

1. **Updated UserType Enum**: Added `ADMIN = "admin"` to the UserType enumeration in `app/models/user.py`
2. **Created Admin Script**: `create_admin.py` - Interactive script to create admin users
3. **Created SQL Migration**: `migrate_admin_type.sql` - Database migration for adding admin type

## Setup Instructions

### Step 1: Apply Database Migration

The database needs to be updated to accept the 'admin' user type.

#### For PostgreSQL:
```bash
cd /home/chidex-world/Desktop/Chidex/ai\ resume/ai-resume-server
source venv/bin/activate
psql -U your_username -d your_database -f migrate_admin_type.sql
```

Or manually run:
```sql
ALTER TYPE usertype ADD VALUE 'admin';
```

#### For MySQL/MariaDB:
```sql
ALTER TABLE users MODIFY COLUMN user_type ENUM('employee', 'employer', 'admin') NOT NULL;
```

#### For SQLite:
SQLite will automatically handle the enum change via SQLAlchemy. No manual migration needed.

### Step 2: Create Admin User

Run the admin creation script:

```bash
cd /home/chidex-world/Desktop/Chidex/ai\ resume/ai-resume-server
source venv/bin/activate
python create_admin.py
```

The script will prompt you for:
- Email
- First name
- Last name
- Phone (optional)
- Password (minimum 8 characters)
- Password confirmation

Example:
```
=== Create Admin User ===

Enter admin email: admin@example.com
Enter first name: Admin
Enter last name: User
Enter phone (optional):
Enter password (min 8 characters): ********
Confirm password: ********

✓ Admin user created successfully!
  ID: 1
  Email: admin@example.com
  Name: Admin User
  User Type: admin
  Status: Active & Verified
```

### Step 3: Login as Admin

1. Go to the login page: `http://localhost:3000/login`
2. Enter the admin email and password you created
3. You'll be automatically redirected to: `http://localhost:3000/admin/dashboard`

## Converting Existing User to Admin

If you already have a user account and want to convert it to admin, you can:

**Option 1: Use the create_admin.py script**
- Run the script with an existing email
- It will ask if you want to convert the user to admin

**Option 2: Direct SQL Update**
```sql
-- Make sure user_type is lowercase
UPDATE users SET user_type = 'admin', is_verified = true WHERE email = 'your-email@example.com';
```

**Important Note**: The `user_type` column now uses VARCHAR instead of ENUM and values should be lowercase ('admin', 'employee', 'employer').

## Troubleshooting

### Error: "Input should be 'employee' or 'employer'"
This means the database hasn't been migrated yet. Apply the SQL migration from Step 1.

### Error: Database connection timeout
Make sure your database service is running and the connection settings in `.env` are correct.

### Error: "User already exists"
Use the conversion method to change an existing user to admin type.

## Files Modified/Created

- `app/models/user.py` - Added ADMIN to UserType enum, added is_admin property
- `create_admin.py` - Script to create admin users
- `migrate_admin_type.sql` - SQL migration file
- `ADMIN_SETUP.md` - This guide

## Next Steps

After creating an admin user and logging in, you can access:
- `/admin/dashboard` - Admin dashboard
- `/admin/users` - User management
- `/admin/content` - Content moderation
- `/admin/analytics` - System analytics
- `/admin/settings` - System settings
