#!/usr/bin/env python3
"""
Database Index Creation Script for Time Capsule Cloud

This script creates all necessary indexes for optimal database performance.
Run this script after setting up MongoDB to improve query performance.
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

def get_database():
    """Get database connection."""
    load_dotenv()
    uri = os.getenv('MONGO_URI')
    if not uri:
        print("❌ MONGO_URI not found in environment variables")
        sys.exit(1)
    
    client = MongoClient(uri)
    
    # Extract database name from URI or use default
    if '/' in uri.rsplit('?', 1)[0]:
        db_name = uri.rsplit('/', 1)[-1].split('?')[0]
        if db_name and db_name != 'mongodb' and ':' not in db_name:
            return client[db_name]
    return client['timecapsule']

def create_indexes():
    """Create all necessary database indexes."""
    db = get_database()
    
    print("🔧 Creating database indexes...")
    print("=" * 50)
    
    # Users collection indexes
    print("\n📋 Creating indexes for 'users' collection...")
    users = db.get_collection('users')
    
    try:
        # Email index (unique)
        users.create_index('email', unique=True, name='email_unique')
        print("  ✅ Created unique index on 'email'")
    except Exception as e:
        print(f"  ⚠️  Index on 'email' may already exist: {e}")

    try:
        # Display name unique index (for unique ID name)
        users.create_index('display_name', unique=True, sparse=True, name='display_name_unique')
        print("  ✅ Created unique index on 'display_name'")
    except Exception as e:
        print(f"  ⚠️  Index on 'display_name' may already exist: {e}")
    
    try:
        users.create_index('created_at', name='created_at_idx')
        print("  ✅ Created index on 'created_at'")
    except Exception as e:
        print(f"  ⚠️  Index on 'created_at' may already exist: {e}")
    
    # Capsules collection indexes
    print("\n📦 Creating indexes for 'capsules' collection...")
    capsules = db.get_collection('capsules')
    
    try:
        capsules.create_index('user_id', name='user_id_idx')
        print("  ✅ Created index on 'user_id'")
    except Exception as e:
        print(f"  ⚠️  Index on 'user_id' may already exist: {e}")

    try:
        capsules.create_index('sender_id', name='sender_id_idx')
        print("  ✅ Created index on 'sender_id'")
    except Exception as e:
        print(f"  ⚠️  Index on 'sender_id' may already exist: {e}")

    try:
        capsules.create_index('recipient_id', name='recipient_id_idx')
        print("  ✅ Created index on 'recipient_id'")
    except Exception as e:
        print(f"  ⚠️  Index on 'recipient_id' may already exist: {e}")
    
    try:
        capsules.create_index('unlock_date', name='unlock_date_idx')
        print("  ✅ Created index on 'unlock_date'")
    except Exception as e:
        print(f"  ⚠️  Index on 'unlock_date' may already exist: {e}")
    
    try:
        capsules.create_index('is_unlocked', name='is_unlocked_idx')
        print("  ✅ Created index on 'is_unlocked'")
    except Exception as e:
        print(f"  ⚠️  Index on 'is_unlocked' may already exist: {e}")
    
    try:
        capsules.create_index('created_at', name='created_at_idx')
        print("  ✅ Created index on 'created_at'")
    except Exception as e:
        print(f"  ⚠️  Index on 'created_at' may already exist: {e}")
    
    try:
        capsules.create_index('capsule_id', unique=True, name='capsule_id_unique')
        print("  ✅ Created unique index on 'capsule_id'")
    except Exception as e:
        print(f"  ⚠️  Index on 'capsule_id' may already exist: {e}")
    
    # Compound indexes for common queries
    print("\n🔗 Creating compound indexes...")
    
    try:
        capsules.create_index(
            [('user_id', 1), ('is_unlocked', 1)],
            name='user_id_is_unlocked_idx'
        )
        print("  ✅ Created compound index on ('user_id', 'is_unlocked')")
    except Exception as e:
        print(f"  ⚠️  Compound index may already exist: {e}")
    
    try:
        capsules.create_index(
            [('user_id', 1), ('created_at', -1)],
            name='user_id_created_at_idx'
        )
        print("  ✅ Created compound index on ('user_id', 'created_at')")
    except Exception as e:
        print(f"  ⚠️  Compound index may already exist: {e}")
    
    try:
        # For scheduler queries
        capsules.create_index(
            [('is_unlocked', 1), ('unlock_date', 1)],
            name='scheduler_query_idx'
        )
        print("  ✅ Created compound index for scheduler queries")
    except Exception as e:
        print(f"  ⚠️  Compound index may already exist: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Index creation completed!")
    print("\n📊 Index Summary:")
    
    # List all indexes
    print("\nUsers collection indexes:")
    for idx in users.list_indexes():
        print(f"  - {idx['name']}")
    
    print("\nCapsules collection indexes:")
    for idx in capsules.list_indexes():
        print(f"  - {idx['name']}")

    # Notifications
    print("\n🔔 Creating indexes for 'notifications' collection...")
    notifications = db.get_collection('notifications')
    try:
        notifications.create_index('user_id', name='notif_user_id_idx')
        notifications.create_index('created_at', name='notif_created_at_idx')
        notifications.create_index('read', name='notif_read_idx')
        print("  ✅ Created indexes on notifications")
    except Exception as e:
        print(f"  ⚠️  Notifications indexes may already exist: {e}")

if __name__ == '__main__':
    try:
        create_indexes()
    except Exception as e:
        print(f"\n❌ Error creating indexes: {e}")
        sys.exit(1)





