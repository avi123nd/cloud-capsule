"""
Scheduler Service using MongoDB.

Responsible for periodically checking capsules that should be unlocked and
triggering both in-app and email notifications on release day.

This service runs inside Flask application context to ensure proper
access to database connections and email services.
"""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from bson import ObjectId

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Scheduler service for automated capsule unlocking and notifications.
    
    This service runs scheduled jobs that:
    1. Find capsules ready to unlock (unlock_date has passed)
    2. Unlock capsules automatically
    3. Send email notifications to recipients
    4. Create in-app notifications
    """
    
    def __init__(self, db, capsule_service, email_service=None, app=None):
        """
        Initialize the scheduler service.
        
        Args:
            db: MongoDB database instance
            capsule_service: CapsuleService instance
            email_service: EmailService instance (optional, will create if not provided)
            app: Flask application instance (required for app context)
        """
        self.db = db
        self.capsules = db.get_collection('capsules')
        self.capsule_service = capsule_service
        self.email_service = email_service
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        
        # Validate Flask app is provided
        if app is None:
            logger.warning("SchedulerService initialized without Flask app - emails may fail")
    
    def start_scheduler(self):
        """
        Start the background scheduler for capsule unlock checks.
        
        Schedule:
        - Hourly check: Every hour at minute 0
        - Daily check: Every day at midnight (00:00)
        """
        if not self.is_running:
            # Add hourly job - runs at the start of every hour
            self.scheduler.add_job(
                func=self._run_hourly_check,
                trigger=CronTrigger(minute=0),
                id='hourly_capsule_check',
                name='Hourly Capsule Unlock Check',
                replace_existing=True,
            )
            
            # Add daily job - runs at midnight every day
            self.scheduler.add_job(
                func=self._run_daily_check,
                trigger=CronTrigger(hour=0, minute=0),
                id='daily_capsule_check',
                name='Daily Capsule Unlock Check',
                replace_existing=True,
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info('Scheduler started successfully - jobs scheduled for hourly and daily checks')
    
    def stop_scheduler(self):
        """Stop the background scheduler."""
        if self.is_running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info('Scheduler stopped')
    
    def _run_hourly_check(self):
        """
        Hourly check wrapper that runs inside Flask app context.
        
        This wrapper ensures that all operations have access to Flask context.
        """
        if self.app:
            with self.app.app_context():
                self.check_and_unlock_capsules(hourly=True)
        else:
            # Fallback if no Flask app - run directly (may have issues)
            logger.warning("Running scheduler without Flask app context")
            self.check_and_unlock_capsules(hourly=True)
    
    def _run_daily_check(self):
        """
        Daily check wrapper that runs inside Flask app context.
        
        This wrapper ensures that all operations have access to Flask context.
        """
        if self.app:
            with self.app.app_context():
                self.check_and_unlock_capsules(hourly=False)
        else:
            # Fallback if no Flask app - run directly (may have issues)
            logger.warning("Running scheduler without Flask app context")
            self.check_and_unlock_capsules(hourly=False)
    
    def check_and_unlock_capsules(self, hourly: bool = False):
        """
        Main job that finds and unlocks capsules that are ready.
        
        This method:
        1. Queries MongoDB for capsules with unlock_date <= now and is_unlocked = False
        2. Unlocks each capsule via capsule_service
        3. Creates in-app notifications
        4. Sends email notifications to recipients
        
        Args:
            hourly: Whether this is an hourly check (for logging purposes)
        """
        try:
            current_time = datetime.utcnow()
            logger.info(f"[{'Hourly' if hourly else 'Daily'} Check] Scanning for capsules ready to unlock at {current_time.isoformat()}")
            
            # Query: capsules that are NOT unlocked AND have unlock_date <= now
            query = {
                'is_unlocked': False,
                'unlock_date': {'$lte': current_time}
            }
            
            cursor = self.capsules.find(query)
            count = 0
            unlock_count = 0
            email_count = 0
            
            for doc in cursor:
                count += 1
                capsule_id = doc.get('capsule_id')
                recipient_email = doc.get('recipient_email')
                recipient_id = doc.get('recipient_id')
                sender_id = doc.get('sender_id') or doc.get('user_id')
                
                try:
                    # Step 1: Unlock the capsule
                    self.capsule_service.unlock_capsule(capsule_id)
                    unlock_count += 1
                    logger.info(f"[Capsule {capsule_id}] Successfully unlocked")
                    
                    # Step 2: Create in-app notification
                    self._create_notification(doc, capsule_id, recipient_id, sender_id)
                    
                    # Step 3: Send email notification
                    email_sent = self._send_unlock_email(doc, capsule_id, recipient_id, sender_id, recipient_email)
                    if email_sent:
                        email_count += 1
                        
                except Exception as e:
                    logger.error(f"[Capsule {capsule_id}] Failed to process: {str(e)}")
                    continue
            
            logger.info(
                f"[{'Hourly' if hourly else 'Daily'} Check] Complete. "
                f"Found {count} capsules, unlocked {unlock_count}, emails sent: {email_count}"
            )
            
        except Exception as e:
            logger.error(f"[{'Hourly' if hourly else 'Daily'} Check] Critical error: {str(e)}")
            raise
    
    def _create_notification(self, doc, capsule_id, recipient_id, sender_id):
        """
        Create an in-app notification for the capsule recipient.
        
        Args:
            doc: Capsule document from MongoDB
            capsule_id: The capsule ID
            recipient_id: Recipient user ID
            sender_id: Sender user ID
        """
        try:
            notifications = self.db.get_collection('notifications')
            
            # Determine notification message
            notification_message = 'You received a capsule released today'
            if not recipient_id:
                notification_message = 'Your capsule is now available'
                recipient_id = sender_id
            
            # Only create notification for registered users
            if recipient_id:
                notifications.insert_one({
                    'user_id': recipient_id,
                    'type': 'capsule_release',
                    'capsule_id': capsule_id,
                    'sender_id': sender_id,
                    'created_at': datetime.utcnow(),
                    'read': False,
                    'message': notification_message
                })
                logger.info(f"[Notification] Created for user {recipient_id}")
                
        except Exception as e:
            logger.error(f"[Notification] Failed to create: {str(e)}")
    
    def _send_unlock_email(self, doc, capsule_id, recipient_id, sender_id, recipient_email) -> bool:
        """
        Send unlock notification email to the recipient.
        
        Args:
            doc: Capsule document from MongoDB
            capsule_id: The capsule ID
            recipient_id: Recipient user ID
            sender_id: Sender user ID
            recipient_email: External recipient email (if any)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            users = self.db.get_collection('users')
            
            # Determine recipient email and name
            target_email = None
            target_name = None
            sender_name = None
            
            # First priority: external recipient email (non-registered user)
            if recipient_email:
                target_email = recipient_email
                logger.info(f"[Email] Sending to external recipient: {target_email}")
            
            # Second priority: look up registered user
            elif recipient_id:
                # Handle ObjectId conversion
                if isinstance(recipient_id, str):
                    try:
                        recipient_obj_id = ObjectId(recipient_id)
                        recipient_doc = users.find_one({'_id': recipient_obj_id})
                    except Exception:
                        recipient_doc = None
                else:
                    recipient_doc = users.find_one({'_id': recipient_id})
                
                if recipient_doc:
                    target_email = recipient_doc.get('email')
                    target_name = recipient_doc.get('display_name')
                    logger.info(f"[Email] Sending to registered user: {target_name} ({target_email})")
            
            # Get sender name
            if sender_id:
                if isinstance(sender_id, str):
                    try:
                        sender_obj_id = ObjectId(sender_id)
                        sender_doc = users.find_one({'_id': sender_obj_id})
                    except Exception:
                        sender_doc = None
                else:
                    sender_doc = users.find_one({'_id': sender_id})
                
                if sender_doc:
                    sender_name = sender_doc.get('display_name')
            
            # Send email if we have an address
            if target_email and self.email_service:
                unlock_date = doc.get('unlock_date')
                self.email_service.send_capsule_unlocked_notification(
                    recipient_email=target_email,
                    recipient_name=target_name,
                    sender_name=sender_name,
                    unlock_date=unlock_date,
                )
                logger.info(f"[Email] Successfully sent unlock notification to {target_email}")
                return True
            elif not target_email:
                logger.warning(f"[Email] No recipient email found for capsule {capsule_id}")
                return False
            else:
                logger.warning(f"[Email] Email service not configured")
                return False
                
        except Exception as e:
            logger.error(f"[Email] Failed to send unlock notification: {str(e)}")
            return False
    
    def force_unlock_capsule(self, capsule_id: str):
        """
        Manually unlock a capsule (bypasses scheduler).
        
        Args:
            capsule_id: The ID of the capsule to unlock
            
        Returns:
            dict: Unlock result from capsule_service
        """
        return self.capsule_service.unlock_capsule(capsule_id)
    
    def get_scheduler_status(self):
        """
        Get the current status of the scheduler and its jobs.
        
        Returns:
            dict: Status information including running state and job details
        """
        jobs = []
        if self.is_running:
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger),
                })
        
        return {
            'is_running': self.is_running,
            'jobs': jobs,
            'job_count': len(jobs)
        }
