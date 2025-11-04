# Alembic Database Migration Guide

This guide covers the essential Alembic commands for managing database migrations in this FastAPI project.

## 📋 Table of Contents

- [What is Alembic?](#what-is-alembic)
- [Initial Setup (Already Done)](#initial-setup-already-done)
- [Common Commands](#common-commands)
- [Creating Migrations](#creating-migrations)
- [Applying Migrations](#applying-migrations)
- [Rolling Back Migrations](#rolling-back-migrations)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## What is Alembic?

Alembic is a database migration tool for SQLAlchemy. It allows you to:

- Track database schema changes over time
- Apply changes to databases in a controlled, versioned manner
- Roll back changes if needed
- Keep development, staging, and production databases in sync

## Initial Setup (Already Done)

Your Alembic is already configured! Here's what was set up:

1. ✅ Alembic initialized in the `alembic/` directory
2. ✅ `alembic.ini` configured to use your database URL from environment variables
3. ✅ `alembic/env.py` configured to import your SQLAlchemy models
4. ✅ Initial migration created and stamped

## Common Commands

### Check Current Migration Version

```bash
alembic current
```

Shows which migration version your database is currently at.

### View Migration History

```bash
alembic history
```

Shows all available migrations and their relationships.

### View Migration History (Verbose)

```bash
alembic history --verbose
```

Shows detailed information about each migration.

## Creating Migrations

### Auto-generate Migration from Model Changes

When you modify your SQLAlchemy models (add/remove columns, tables, etc.), create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

**Example:**

```bash
alembic revision --autogenerate -m "Add email column to users table"
```

**Important:** Always review the auto-generated migration file before applying it!

### Create Empty Migration (Manual)

For custom operations or data migrations:

```bash
alembic revision -m "Description"
```

**Example:**

```bash
alembic revision -m "Populate default categories"
```

## Applying Migrations

### Upgrade to Latest Version

```bash
alembic upgrade head
```

Applies all pending migrations to bring your database to the latest schema.

### Upgrade by One Step

```bash
alembic upgrade +1
```

Applies only the next pending migration.

### Upgrade to Specific Version

```bash
alembic upgrade <revision_id>
```

**Example:**

```bash
alembic upgrade b573df09ec59
```

## Rolling Back Migrations

### Downgrade by One Step

```bash
alembic downgrade -1
```

Rolls back the most recent migration.

### Downgrade to Specific Version

```bash
alembic downgrade <revision_id>
```

**Example:**

```bash
alembic downgrade b573df09ec59
```

### Downgrade to Base (Remove All Migrations)

```bash
alembic downgrade base
```

⚠️ **Warning:** This removes all database tables managed by Alembic!

## Best Practices

### 1. Always Review Auto-Generated Migrations

Before applying, check the migration file in `alembic/versions/`:

```python
def upgrade() -> None:
    # Review these commands carefully
    op.add_column('users', sa.Column('email', sa.String(255), nullable=True))

def downgrade() -> None:
    # Ensure downgrade logic is correct
    op.drop_column('users', 'email')
```

### 2. Test Migrations Locally First

```bash
# Test upgrade
alembic upgrade head

# Test downgrade (if needed)
alembic downgrade -1

# Re-apply
alembic upgrade head
```

### 3. Commit Migrations with Code Changes

When you change models:

1. Update your SQLAlchemy models
2. Generate migration: `alembic revision --autogenerate -m "Description"`
3. Review the migration file
4. Test locally
5. Commit both model changes and migration file together

### 4. Never Edit Applied Migrations

Once a migration is applied to any database (especially production), never edit it. Create a new migration instead.

### 5. Use Descriptive Migration Messages

❌ Bad:

```bash
alembic revision --autogenerate -m "update"
```

✅ Good:

```bash
alembic revision --autogenerate -m "Add user_role column and role enum to users table"
```

## Workflow Example

### Scenario: Adding a new field to User model

1. **Update the model** (`models/user.py`):

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    # New field added
    phone_number = Column(String(20), nullable=True)
```

2. **Generate migration**:

```bash
alembic revision --autogenerate -m "Add phone_number to users"
```

3. **Review generated migration** in `alembic/versions/`:

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'phone_number')
```

4. **Apply migration**:

```bash
alembic upgrade head
```

5. **Verify**:

```bash
alembic current
```

## Troubleshooting

### Issue: "Target database is not up to date"

**Solution:**

```bash
alembic upgrade head
```

### Issue: "Can't locate revision identified by <revision_id>"

**Solution:** Check if the migration file exists in `alembic/versions/`. If working with multiple developers, pull latest changes.

### Issue: Migration conflict (multiple heads)

**Solution:**

```bash
# View the conflict
alembic heads

# Merge the heads
alembic merge -m "Merge migrations" <head1> <head2>
```

### Issue: Database out of sync with migrations

**Solution (Caution):**

```bash
# Stamp the database at current state
alembic stamp head
```

### Issue: Need to drop all tables and start fresh (Development only!)

```bash
# Downgrade to base
alembic downgrade base

# Upgrade to latest
alembic upgrade head
```

## Current Migration Status

Your project currently has:

- ✅ Initial migration: `b573df09ec59` - "Initial migration"
- ✅ Database stamped at `head`
- ✅ Models: User, Category, Item

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

**Happy Migrating! 🚀**
