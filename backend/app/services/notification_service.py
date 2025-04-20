import logging
import os
import re
from twilio.rest import Client
from app.db import mongo
from bson.objectid import ObjectId
from flask_smorest import abort

# Create logger for this module
logger = logging.getLogger(__name__)

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM")

def strip_html_tags(text):
    """
    Remove HTML tags from text
    
    Args:
        text (str): Text that may contain HTML tags
        
    Returns:
        str: Text with HTML tags removed
    """
    if not text:
        return ""
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Replace common HTML entities
    clean_text = clean_text.replace('&nbsp;', ' ')
    clean_text = clean_text.replace('&amp;', '&')
    clean_text = clean_text.replace('&lt;', '<')
    clean_text = clean_text.replace('&gt;', '>')
    clean_text = clean_text.replace('&quot;', '"')
    clean_text = clean_text.replace('&#39;', "'")
    
    # Remove multiple consecutive whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text

def send_whatsapp_notification(to_number, message):
    """
    Send WhatsApp message using Twilio
    
    Args:
        to_number (str): The phone number to send the message to (with country code)
        message (str): The message content
        
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_WHATSAPP_FROM:
        logger.error("Twilio credentials not configured")
        return False

    try:
        # Format the 'to' number for WhatsApp
        to_whatsapp_number = format_phone_number(to_number)
        
        # Create Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send message
        message = client.messages.create(
            from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
            body=message,
            to=f"whatsapp:{to_whatsapp_number}"
        )
        
        logger.info(f"WhatsApp message sent successfully: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {str(e)}")
        return False

def format_phone_number(phone_number):
    """
    Format phone number for WhatsApp
    
    Args:
        phone_number (str or int): The phone number to format
        
    Returns:
        str: Formatted phone number
    """
    # Ensure phone_number is a string
    if not isinstance(phone_number, str):
        phone_number = str(phone_number)
    
    # Remove any non-digit characters
    digits_only = ''.join(filter(str.isdigit, phone_number))
    
    # If no country code (assuming Indian numbers), add +91
    if len(digits_only) <= 10:
        return f"+91{digits_only[-10:]}"
    
    # If it already has country code, ensure it starts with +
    return f"+{digits_only}" if not digits_only.startswith('+') else digits_only

def notify_all_candidates_about_new_job(job_name, job_description):
    """
    Send WhatsApp notification to all candidates about a new job
    
    Args:
        job_name (str): The name of the new job
        job_description (str): The job description
        
    Returns:
        dict: Stats about notification sending
    """
    # Get all candidates with phone numbers
    collection = mongo.db.candidate
    candidates = collection.find({}, {"candidate_name": 1, "phone_number": 1, "has_resume": 1})
    
    sent_count = 0
    failed_count = 0
    
    # Clean job description from any HTML tags
    clean_description = strip_html_tags(job_description)
    
    # Prepare the message
    job_message = f"🔔 *New Job Alert!*\n\n*Position:* {job_name}\n\n*Description:* {clean_description}\n\n Drop your updated resume to apply for this job or else your old resume will be considered for this job."
    
    # Send notification to each candidate
    for candidate in candidates:
        if candidate.get("phone_number"):
            # Add resume instruction for candidates without resumes
            message = job_message
            if candidate.get("has_resume") is False:
                message += "\n\n*Note:* We noticed you haven't uploaded your resume yet. Simply reply to this message with your resume attached as a PDF or DOCX file to complete your profile and be considered for this position."
            
            success = send_whatsapp_notification(
                candidate["phone_number"], 
                message
            )
            if success:
                sent_count += 1
            else:
                failed_count += 1
    
    return {
        "sent": sent_count,
        "failed": failed_count,
        "total": sent_count + failed_count
    }

def send_shortlist_notifications(job_name, top_n=5):
    """
    Send WhatsApp notification to top N candidates for a specific job
    
    Args:
        job_name (str): The name of the job
        top_n (int): Number of top candidates to notify
        
    Returns:
        dict: Stats about notification sending
    """
    try:
        # Get the job details
        job = mongo.db.job.find_one_or_404({"job_name": job_name})
        job_id = job["_id"]
        
        # Get all candidates with their matching scores for this job
        collection_candidate = mongo.db.candidate
        results = []

        for candidate in collection_candidate.find():
            matching = mongo.db.matching.find_one(
                {"job_id": job_id, "candidate_id": candidate["_id"]}
            )

            if matching is not None:
                results.append({
                    "candidate_id": candidate["_id"],
                    "candidate_name": candidate["candidate_name"],
                    "candidate_email": candidate["email"],
                    "candidate_phone": candidate["phone_number"],
                    "score": matching["score"]
                })

        # Sort results by score in descending order and limit to specified number of candidates
        top_candidates = sorted(results, key=lambda x: int(x["score"]), reverse=True)[:top_n]
        
        sent_count = 0
        failed_count = 0
        
        # Clean job description from any HTML tags
        clean_description = strip_html_tags(job["job_description"])
        
        # Send notification to each shortlisted candidate
        for candidate in top_candidates:
            if candidate.get("candidate_phone"):
                # Prepare the message with shortlist notification
                message = (
                    f"🎉 *Congratulations {candidate['candidate_name']}!* 🎉\n\n"
                    f"You have been shortlisted for the *{job_name}* position.\n\n"
                    f"*Position:* {job_name}\n"
                    f"*Description:* {clean_description[:200]}...\n\n"
                    f"Our team will contact you soon for the next steps in the selection process.\n\n"
                    f"Best regards,\nThe Hiring Team"
                )
                
                success = send_whatsapp_notification(
                    candidate["candidate_phone"],
                    message
                )
                
                if success:
                    # Update database to mark candidate as notified
                    mongo.db.matching.update_one(
                        {"job_id": job_id, "candidate_id": candidate["candidate_id"]},
                        {"$set": {"shortlist_notified": True}}
                    )
                    sent_count += 1
                else:
                    failed_count += 1
        
        return {
            "sent": sent_count,
            "failed": failed_count,
            "total": sent_count + failed_count
        }
        
    except Exception as e:
        logger.error(f"Failed to send shortlist notifications: {str(e)}")
        abort(500, message="Failed to send shortlist notifications") 