"""
Dashboard Routes (MongoDB)
"""

from flask import Blueprint, request, jsonify
from services.auth_service import require_auth
from services.encryption_service import EncryptionService
from services.capsule_service import CapsuleService
from pymongo import MongoClient
import os
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

def get_db():
    uri = os.getenv('MONGO_URI')
    client = MongoClient(uri)
    if '/' in uri.rsplit('?', 1)[0]:
        db_name = uri.rsplit('/', 1)[-1].split('?')[0]
        if db_name and db_name != 'mongodb' and ':' not in db_name:
            return client[db_name]
    return client['timecapsule']

_db = get_db()
_encryption = EncryptionService()
_capsules = CapsuleService(_db, _encryption)


@dashboard_bp.route('/dashboard', methods=['GET'])
@require_auth
def get_dashboard():
    try:
        user_id = request.user['uid']
        include_locked = request.args.get('include_locked', 'true').lower() == 'true'
        capsules = _capsules.get_user_capsules(user_id, include_locked)
        locked_capsules = [c for c in capsules if not c.get('is_unlocked', False)]
        unlocked_capsules = [c for c in capsules if c.get('is_unlocked', False)]
        total_capsules = len(capsules)
        locked_count = len(locked_capsules)
        unlocked_count = len(unlocked_capsules)
        current_time = datetime.utcnow()
        week_from_now = current_time + timedelta(days=7)
        upcoming_unlocks = []
        for c in locked_capsules:
            unlock_date = c.get('unlock_date')
            if unlock_date:
                # Convert string to datetime if needed
                if isinstance(unlock_date, str):
                    try:
                        unlock_date_str = unlock_date.replace('Z', '+00:00')
                        unlock_date = datetime.fromisoformat(unlock_date_str)
                    except (ValueError, AttributeError):
                        try:
                            unlock_date = datetime.fromisoformat(unlock_date)
                        except (ValueError, AttributeError):
                            continue
                # Compare datetime objects
                if isinstance(unlock_date, datetime) and unlock_date <= week_from_now:
                    upcoming_unlocks.append(c)
        return jsonify({
            'user_id': user_id,
            'statistics': {
                'total_capsules': total_capsules,
                'locked_capsules': locked_count,
                'unlocked_capsules': unlocked_count,
                'upcoming_unlocks': len(upcoming_unlocks)
            },
            'locked_capsules': locked_capsules,
            'unlocked_capsules': unlocked_capsules,
            'upcoming_unlocks': upcoming_unlocks
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/dashboard/unlocked', methods=['GET'])
@require_auth
def get_unlocked_capsules():
    try:
        user_id = request.user['uid']
        capsules = _capsules.get_user_capsules(user_id, include_locked=False)
        return jsonify({'unlocked_capsules': capsules, 'count': len(capsules)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/dashboard/upcoming', methods=['GET'])
@require_auth
def get_upcoming_unlocks():
    try:
        user_id = request.user['uid']
        capsules = _capsules.get_user_capsules(user_id, include_locked=True)
        locked_capsules = [c for c in capsules if not c.get('is_unlocked', False)]
        current_time = datetime.utcnow()
        week_from_now = current_time + timedelta(days=7)
        upcoming_unlocks = []
        for c in locked_capsules:
            unlock_date = c.get('unlock_date')
            if unlock_date:
                # Convert string to datetime if needed
                if isinstance(unlock_date, str):
                    try:
                        unlock_date_str = unlock_date.replace('Z', '+00:00')
                        unlock_date = datetime.fromisoformat(unlock_date_str)
                    except (ValueError, AttributeError):
                        try:
                            unlock_date = datetime.fromisoformat(unlock_date)
                        except (ValueError, AttributeError):
                            continue
                # Compare datetime objects
                if isinstance(unlock_date, datetime) and unlock_date <= week_from_now:
                    upcoming_unlocks.append(c)
        # Sort by unlock_date, handling both string and datetime formats
        def get_unlock_date_for_sort(c):
            unlock_date = c.get('unlock_date')
            if not unlock_date:
                return datetime.max
            if isinstance(unlock_date, str):
                try:
                    unlock_date_str = unlock_date.replace('Z', '+00:00')
                    return datetime.fromisoformat(unlock_date_str)
                except (ValueError, AttributeError):
                    try:
                        return datetime.fromisoformat(unlock_date)
                    except (ValueError, AttributeError):
                        return datetime.max
            return unlock_date if isinstance(unlock_date, datetime) else datetime.max
        upcoming_unlocks.sort(key=get_unlock_date_for_sort)
        return jsonify({'upcoming_unlocks': upcoming_unlocks, 'count': len(upcoming_unlocks)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/dashboard/stats', methods=['GET'])
@require_auth
def get_dashboard_stats():
    try:
        user_id = request.user['uid']
        capsules = _capsules.get_user_capsules(user_id, include_locked=True)
        total_capsules = len(capsules)
        locked_capsules = [c for c in capsules if not c.get('is_unlocked', False)]
        unlocked_capsules = [c for c in capsules if c.get('is_unlocked', False)]
        type_counts = {}
        for c in capsules:
            t = c.get('capsule_type', 'unknown')
            type_counts[t] = type_counts.get(t, 0) + 1
        current_time = datetime.utcnow()
        week_from_now = current_time + timedelta(days=7)
        
        # Handle unlock_date which might be a string (ISO format) or datetime
        upcoming_count = 0
        for c in locked_capsules:
            unlock_date = c.get('unlock_date')
            if unlock_date:
                # Convert string to datetime if needed
                if isinstance(unlock_date, str):
                    try:
                        # Handle ISO format strings
                        unlock_date_str = unlock_date.replace('Z', '+00:00')
                        unlock_date = datetime.fromisoformat(unlock_date_str)
                    except (ValueError, AttributeError):
                        try:
                            # Fallback for other formats
                            unlock_date = datetime.fromisoformat(unlock_date)
                        except (ValueError, AttributeError):
                            continue
                # Compare datetime objects
                if isinstance(unlock_date, datetime) and unlock_date <= week_from_now:
                    upcoming_count += 1
        
        return jsonify({
            'total_capsules': total_capsules,
            'locked_capsules': len(locked_capsules),
            'unlocked_capsules': len(unlocked_capsules),
            'upcoming_unlocks': upcoming_count,
            'type_breakdown': type_counts
        }), 200
    except Exception as e:
        import traceback
        print(f"Error in get_dashboard_stats: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
