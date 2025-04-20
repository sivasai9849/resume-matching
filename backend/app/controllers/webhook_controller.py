import logging
import tempfile
import os
import requests
from flask import request, jsonify, Response
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.db import mongo
from app.services import candidate_service
from bson.objectid import ObjectId
from twilio.twiml.messaging_response import MessagingResponse
from werkzeug.utils import secure_filename
import config

# Create logger for this module
logger = logging.getLogger(__name__)

blp = Blueprint("Webhook", __name__, description="Webhook API")


@blp.route("/webhook/twilio")
class TwilioWebhook(MethodView):
    def post(self):
        try:
            # Extract data from the Twilio WhatsApp webhook
            from_number = request.values.get('From', '').replace('whatsapp:+', '')
            body = request.values.get('Body', '')
            num_media = int(request.values.get('NumMedia', 0))
            
            logger.info(f"Received WhatsApp message from {from_number}")
            logger.info(f"Message body: {body}")
            logger.info(f"Number of media items: {num_media}")
            
            # Create a TwiML response
            resp = MessagingResponse()
            from_number = int(from_number)
            # Find the candidate based on the phone number
            candidate = mongo.db.candidate.find_one({"phone_number": from_number})
            
            if not candidate:
                # Try without the "+" in case the phone number format is different
                candidate = mongo.db.candidate.find_one({"phone_number": from_number})
            
            
            if not candidate:
                logger.warning(f"No candidate found for phone number: {from_number}")
                resp.message("Sorry, we couldn't find your profile in our system. Please contact support.")
                return Response(str(resp), mimetype='text/xml')
            
            logger.info(f"Found candidate: {candidate['candidate_name']}")
            
            # Check if there's a resume attached
            if num_media > 0:
                media_files = []
                
                # Process each media item (we expect only one resume, but handle multiple just in case)
                for i in range(num_media):
                    media_url = request.values.get(f'MediaUrl{i}')
                    content_type = request.values.get(f'MediaContentType{i}')
                    
                    logger.info(f"Media URL: {media_url}")
                    logger.info(f"Content Type: {content_type}")
                    
                    # Only accept PDF or DOCX files
                    if content_type not in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                        resp.message("Sorry, we only accept PDF or DOCX files as resumes. Please send your resume in one of these formats.")
                        return Response(str(resp), mimetype='text/xml')
                    
                    # Download the file
                    try:
                        # Use Twilio credentials for authentication
                        twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
                        twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
                        
                        if not twilio_account_sid or not twilio_auth_token:
                            twilio_account_sid = config.TWILIO_ACCOUNT_SID
                            twilio_auth_token = config.TWILIO_AUTH_TOKEN
                        
                        # Make authenticated request to download media
                        media_response = requests.get(
                            media_url,
                            auth=(twilio_account_sid, twilio_auth_token)
                        )
                        
                        if media_response.status_code != 200:
                            logger.error(f"Failed to download media: HTTP {media_response.status_code}")
                            resp.message("Sorry, we had trouble downloading your resume. Please try again later.")
                            return Response(str(resp), mimetype='text/xml')
                        
                        # Create a temporary file with the correct extension
                        suffix = '.pdf' if content_type == 'application/pdf' else '.docx'
                        
                        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
                            temp_file.write(media_response.content)
                            temp_path = temp_file.name
                        
                        media_files.append({
                            'path': temp_path,
                            'content_type': content_type,
                            'filename': f"resume_{candidate['_id']}{suffix}"
                        })
                        
                    except Exception as e:
                        logger.error(f"Error downloading media: {str(e)}")
                        resp.message("Sorry, we had trouble processing your resume. Please try again later.")
                        return Response(str(resp), mimetype='text/xml')
                
                # Process the resume(s)
                for media_file in media_files:
                    try:
                        # Update the candidate to indicate they have a resume
                        mongo.db.candidate.update_one(
                            {"_id": candidate["_id"]},
                            {"$set": {"has_resume": True}}
                        )
                        
                        # Open the temporary file and process it
                        with open(media_file['path'], 'rb') as file:
                            from werkzeug.datastructures import FileStorage
                            file_storage = FileStorage(
                                stream=file,
                                filename=media_file['filename'],
                                content_type=media_file['content_type']
                            )
                            
                            # Process the resume using the existing service with the candidate ID
                            candidate_service.process_upload_file(
                                file_storage, 
                                str(candidate["_id"])
                            )
                            
                            # Delete the temporary file
                            os.unlink(media_file['path'])
                            
                            
                    except Exception as e:
                        logger.error(f"Error processing resume: {str(e)}")
                        
                        # Try to clean up temporary files
                        try:
                            os.unlink(media_file['path'])
                        except:
                            pass
                        
                        resp.message("Sorry, we had trouble analyzing your resume. Please try again later or contact support.")
                        return Response(str(resp), mimetype='text/xml')
                
                # Send a success message
                resp.message(f"Thank you, {candidate['candidate_name']}! Your resume has been received and processed successfully. We'll match you with suitable job opportunities soon.")
                
            else:
                # No media, just text
                resp.message(f"Hello {candidate['candidate_name']}! To complete your profile, please send us your resume as a PDF or DOCX file.")
            
            return Response(str(resp), mimetype='text/xml')
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            resp = MessagingResponse()
            resp.message("Sorry, something went wrong. Please try again later.")
            return Response(str(resp), mimetype='text/xml') 