"""
Notification Routes - in-app notifications (no email)
"""

from flask import Blueprint, request, jsonify
from services.auth_service import require_auth
from pymongo import MongoClient
import os
from datetime import datetime, timedelta

notifications_bp = Blueprint('notifications', __name__)


def get_db():
    uri = os.getenv('MONGO_URI')
    client = MongoClient(uri)
    if '/' in uri.rsplit('?', 1)[0]:
        db_name = uri.rsplit('/', 1)[-1].split('?')[0]
        if db_name and db_name != 'mongodb' and ':' not in db_name:
            return client[db_name]
    return client['timecapsule']


_db = get_db()


@notifications_bp.route('/notifications', methods=['GET'])
@require_auth
def list_notifications():
    """List notifications for current user. Optional filters: unread=1, today=1"""
    user_id = request.user['uid']
    unread = request.args.get('unread') == '1'
    today = request.args.get('today') == '1'

    query = {'user_id': user_id}
    if unread:
        query['read'] = False
    if today:
        start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        query['created_at'] = {'$gte': start, '$lt': end}

    results = []
    for doc in _db.get_collection('notifications').find(query).sort('created_at', -1):
        item = {
            'id': str(doc['_id']),
            'user_id': doc['user_id'],
            'type': doc.get('type'),
            'capsule_id': doc.get('capsule_id'),
            'sender_id': doc.get('sender_id'),
            'message': doc.get('message'),
            'created_at': doc.get('created_at').isoformat() if doc.get('created_at') else None,
            'read': doc.get('read', False),
        }
        results.append(item)

    return jsonify({'notifications': results}), 200


@notifications_bp.route('/notifications/<notification_id>/read', methods=['POST'])
@require_auth
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    from bson import ObjectId
    user_id = request.user['uid']
    result = _db.get_collection('notifications').update_one(
        {'_id': ObjectId(notification_id), 'user_id': user_id},
        {'$set': {'read': True, 'read_at': datetime.utcnow()}}
    )
    if result.modified_count == 0:
        return jsonify({'error': 'Notification not found'}), 404
    return jsonify({'message': 'Notification marked as read'}), 200


