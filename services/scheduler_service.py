"""
Scheduler Service using MongoDB.

Responsible for periodically checking capsules that should be unlocked and
triggering both in-app and email notifications on release day.
"""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from services.email_service import EmailService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self, db, capsule_service, email_service: EmailService | None = None):
        self.db = db
        self.capsules = db.get_collection('capsules')
        self.capsule_service = capsule_service
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        # Reuse shared EmailService if provided, otherwise create a local one
        self.email_service = email_service or EmailService()

    def start_scheduler(self):
        if not self.is_running:
            self.scheduler.add_job(
                func=self.check_and_unlock_capsules,
                trigger=CronTrigger(hour=0, minute=0),
                id='daily_capsule_check',
                name='Daily Capsule Unlock Check',
                replace_existing=True,
            )
            self.scheduler.add_job(
                func=self.check_and_unlock_capsules,
                trigger=CronTrigger(minute=0),
                id='hourly_capsule_check',
                name='Hourly Capsule Unlock Check',
                replace_existing=True,
            )
            self.scheduler.start()
            self.is_running = True
            logger.info('Scheduler started successfully')

    def stop_scheduler(self):
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info('Scheduler stopped')

    def check_and_unlock_capsules(self):
        try:
            current_time = datetime.utcnow()
            cursor = self.capsules.find({'is_unlocked': False, 'unlock_date': {'$lte': current_time}})
            count = 0
            for doc in cursor:
                try:
                    self.capsule_service.unlock_capsule(doc['capsule_id'])
                    count += 1
                    logger.info(f"Unlocked capsule: {doc['capsule_id']}")
                    # Create in-app notification(s) on release day
                    try:
                        notifications = self.db.get_collection('notifications')
                        users = self.db.get_collection('users')

                        # Determine who to notify in-app (recipient preferred, else sender)
                        recipient_user_id = None
                        notification_message = ''

                        if doc.get('recipient_id'):
                            recipient_user_id = doc['recipient_id']
                            notification_message = 'You received a capsule released today'
                        else:
                            recipient_user_id = doc.get('sender_id') or doc.get('user_id')
                            notification_message = 'Your capsule is now available'

                        # Create in-app notification ONLY for registered users
                        if recipient_user_id:
                            notifications.insert_one({
                                'user_id': recipient_user_id,
                                'type': 'capsule_release',
                                'capsule_id': doc['capsule_id'],
                                'sender_id': doc.get('sender_id'),
                                'created_at': datetime.utcnow(),
                                'read': False,
                                'message': notification_message
                            })

                        # Send email notification:
                        #  - to registered recipient if we have their user record
                        #  - otherwise to an external recipient_email stored on the capsule
                        try:
                            recipient_email = None
                            recipient_name = None
                            sender_name = None

                            # Prefer external recipient email if stored (non-registered user)
                            if doc.get('recipient_email'):
                                recipient_email = doc['recipient_email']
                            elif recipient_user_id:
                                # Registered user: look up their email + display name
                                recipient_doc = users.find_one({'_id': recipient_user_id})
                                if recipient_doc:
                                    recipient_email = recipient_doc.get('email')
                                    recipient_name = recipient_doc.get('display_name')

                            # Determine sender name if possible
                            sender_id = doc.get('sender_id') or doc.get('user_id')
                            if sender_id:
                                sender_doc = users.find_one({'_id': sender_id})
                                if sender_doc:
                                    sender_name = sender_doc.get('display_name')

                            if recipient_email:
                                self.email_service.send_capsule_unlocked_notification(
                                    recipient_email=recipient_email,
                                    recipient_name=recipient_name,
                                    sender_name=sender_name,
                                    unlock_date=doc.get('unlock_date'),
                                )
                        except Exception as ee:
                            logger.error(
                                "Failed to send email notification for capsule %s: %s",
                                doc['capsule_id'],
                                ee,
                            )
                    except Exception as ne:
                        logger.error(f"Failed to create notification for capsule {doc['capsule_id']}: {ne}")
                except Exception as e:
                    logger.error(f"Failed to unlock capsule {doc['capsule_id']}: {e}")
            logger.info(f"Capsule check complete. Unlocked {count} capsules")
        except Exception as e:
            logger.error(f"Error during unlock check: {e}")

    def force_unlock_capsule(self, capsule_id: str):
        return self.capsule_service.unlock_capsule(capsule_id)

    def get_scheduler_status(self):
        jobs = []
        if self.is_running:
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger),
                })
        return {'is_running': self.is_running, 'jobs': jobs, 'job_count': len(jobs)}
