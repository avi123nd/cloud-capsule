"""
User Routes - search users to send capsules
"""

from flask import Blueprint, request, jsonify
from services.auth_service import require_auth
from pymongo import MongoClient
from bson import ObjectId, regex
import os
import re

user_bp = Blueprint('user', __name__)


def get_db():
    uri = os.getenv('MONGO_URI')
    client = MongoClient(uri)
    if '/' in uri.rsplit('?', 1)[0]:
        db_name = uri.rsplit('/', 1)[-1].split('?')[0]
        if db_name and db_name != 'mongodb' and ':' not in db_name:
            return client[db_name]
    return client['timecapsule']


_db = get_db()


@user_bp.route('/users/search', methods=['GET'])
@require_auth
def search_users():
    """Search users by display name or email. Excludes current user."""
    q = (request.args.get('q') or '').strip()
    if not q:
        return jsonify({'users': []}), 200

    current_uid = request.user['uid']

    # Case-insensitive contains match on display_name or email
    pattern = re.compile(re.escape(q), re.IGNORECASE)
    query = {
        '$and': [
            { '_id': { '$ne': ObjectId(current_uid) } },
            { '$or': [
                { 'display_name': { '$regex': pattern } },
                { 'email': { '$regex': pattern } },
            ]}
        ]
    }

    results = []
    for doc in _db.get_collection('users').find(query).limit(10):
        results.append({
            'uid': str(doc['_id']),
            'email': doc.get('email'),
            'display_name': doc.get('display_name')
        })

    return jsonify({'users': results}), 200


