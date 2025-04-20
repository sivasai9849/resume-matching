import hashlib
import logging
import time
from datetime import datetime
from math import ceil

import config
import requests
from app.db import mongo
from bson.objectid import ObjectId
from flask import request
from flask_smorest import abort
from pytz import timezone
from app.services import notification_service

# Create logger for this module
logger = logging.getLogger(__name__)


def get_candiate(candiate_id):
    collection = mongo.db.candidate
    result = collection.find_one_or_404({"_id": ObjectId(candiate_id)})
    return result


def get_list_candidate(file_data):
    page_size = file_data["page_size"]
    page = file_data["page"]

    if page_size is None:
        page_size = 10

    if page is None:
        page = 1

    try:
        results, total_page, total_file = filter_page(page_size=page_size, page=page)
    except Exception as e:
        logger.error(f"Can not get list file! Error: {str(e)}")
        abort(400, message="Can not get list file!")

    return {"results": results, "total_page": total_page, "total_file": total_file}


def filter_page(page_size=10, page=1):
    # Connect to MongoDB and get the collection
    collection = mongo.db.candidate

    # Count total documents in the collection
    total_file = collection.count_documents({})

    # Calculate total pages
    total_page = ceil(total_file / page_size)

    # Validate page and page_size
    if page < 1 or page_size < 1:
        abort(400, message="Page number or page size is invalid.")

    # Calculate skip and limit values for pagination
    skip = (page - 1) * page_size

    # Retrieve documents with pagination
    results = list(collection.find().skip(skip).limit(page_size))

    return results, total_page, total_file


def update_candidate(candidate_data, candidate_id):
    collection = mongo.db.candidate
    result = collection.update_one(
        {"_id": ObjectId(candidate_id)}, {"$set": candidate_data}
    )
    if result.modified_count == 1:
        return {"message": "Document updated successfully"}
    else:
        return abort("Document not found")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"pdf", "docx"}


def process_upload_file(file, existing_candidate_id=None):
    """
    Process an uploaded resume file
    
    Args:
        file: The uploaded file
        existing_candidate_id: Optional ID of an existing candidate to update
        
    Returns:
        None
    """
    created_at = datetime.now(timezone("Asia/Kolkata")).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Check type pdf or docx
    if not allowed_file(file.filename):
        abort(400, message="Invalid file type. Allowed types: pdf, docx!")

    # Compute the SHA-256 hash of the file contents and convert it to hexadecimal
    filehash = hashlib.sha256(file.read()).hexdigest()

    # Check hashfile (skip if updating existing candidate)
    if not existing_candidate_id and mongo.db.candidate.find_one({"filehash": filehash}):
        abort(400, message=f"CV candidate is exists! File name: {file.filename}")

    # Move the cursor to the beginning of the file
    file.seek(0)

    analysis_endpoint_url = f"{config.ANALYSIS_SERVICE_URL}/candidate/analyse"
    files = {"file": (file.filename, file.stream, file.mimetype)}
    response = requests.post(analysis_endpoint_url, files=files)

    # Check response status and return appropriate response
    if response.status_code != 200:
        abort(400, message=f"Fail to analyse CV candidate! File name: {file.filename}")

    # Get the content of the response
    response_content = response.json()

    response_content["cv_name"] = file.filename
    response_content["created_at"] = created_at
    response_content["filehash"] = filehash
    response_content["has_resume"] = True

    # If we're updating an existing candidate
    if existing_candidate_id:
        try:
            # Get the existing candidate
            collection = mongo.db.candidate
            existing_candidate = collection.find_one({"_id": ObjectId(existing_candidate_id)})
            
            if not existing_candidate:
                logger.error(f"Existing candidate not found: {existing_candidate_id}")
                abort(404, message="Candidate not found")
            
            # Keep some of the original data
            preserved_fields = {
                "candidate_name": existing_candidate.get("candidate_name"),
                "email": existing_candidate.get("email"),
                "phone_number": existing_candidate.get("phone_number"),
                "department": existing_candidate.get("department"),
                "created_at": existing_candidate.get("created_at"),
            }
            
            # Update the response content with preserved fields
            response_content.update(preserved_fields)
            
            # Update the candidate
            result = collection.update_one(
                {"_id": ObjectId(existing_candidate_id)},
                {"$set": response_content}
            )
            
            if result.modified_count != 1:
                logger.error(f"Failed to update candidate: {existing_candidate_id}")
                abort(500, message="Failed to update candidate information")
                
            # Also update any matching records to reflect that the candidate has a resume now
            mongo.db.matching.update_many(
                {"candidate_id": ObjectId(existing_candidate_id)},
                {"$set": {"candidate.has_resume": True}}
            )
            
            logger.info(f"Updated candidate with resume: {existing_candidate_id}")
            
        except Exception as e:
            logger.error(f"Error updating candidate with resume: {str(e)}")
            abort(500, message=f"Error updating candidate with resume: {str(e)}")
    
    # Otherwise, add a new candidate
    else:
        try:
            collection = mongo.db.candidate
            result = collection.insert_one(response_content)
            logger.info(f"New candidate_id: {str(result.inserted_id)}")
        except Exception as e:
            logger.error(f"Upload document to Database failed! Error: {str(e)}")
            abort(400, message="Upload document to Database failed!")

    return None


def upload_file_cv():
    start_time = time.time()
    logger.info(request.files)
    logger.info(request.files.getlist("file_upload"))
    uploaded_files = request.files.getlist("file_upload")

    if len(uploaded_files) == 0:
        abort(400, message="Upload document to Database failed!")

    for file in uploaded_files:
        process_upload_file(file=file)

    logger.info(f"Time upload file: {time.time()-start_time:.2f}")

    return {"message": "File upload successful!"}


def delete_candidate(candidate_id):
    result = mongo.db.candidate.delete_one({"_id": ObjectId(candidate_id)})
    if result.deleted_count == 1:
        # Clean matching
        mongo.db.matching.delete_many({"candidate_id": ObjectId(candidate_id)})

        return {"message": "Document deleted successfully"}
    else:
        return abort("Document not found!")


def bulk_upload_candidates(candidates):
    """
    Bulk upload candidates from Excel
    
    Args:
        candidates (list): List of candidate dictionaries with fields from Excel
    
    Returns:
        dict: A summary of the upload operation
    """
    if not candidates or not isinstance(candidates, list):
        abort(400, message="No valid candidates provided")
    
    required_fields = ["candidate_name", "email", "phone_number", "department"]
    
    # Validate candidates have required fields
    for i, candidate in enumerate(candidates):
        missing_fields = [field for field in required_fields if field not in candidate]
        if missing_fields:
            abort(400, message=f"Candidate at row {i+1} is missing required fields: {', '.join(missing_fields)}")
    
    # Get current timestamp
    created_at = datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare candidates for insertion
    candidates_to_insert = []
    candidates_needing_resume = []
    
    for candidate in candidates:
        # Convert has_resume to boolean if present
        has_resume = False
        if "has_resume" in candidate:
            has_resume_value = str(candidate["has_resume"]).lower()
            has_resume = has_resume_value in ["true", "yes", "1"]
        
        # Create a candidate document with the required structure
        candidate_doc = {
            "candidate_name": candidate["candidate_name"],
            "email": candidate["email"],
            "phone_number": candidate["phone_number"],
            "department": candidate["department"],
            "has_resume": has_resume,
            "comment": candidate.get("comment", ""),  # Use empty string if not provided
            # Initialize empty lists for these fields
            "certificate": [],
            "degree": [],
            "experience": [],
            "technical_skill": [],
            "responsibility": [],
            "soft_skill": [],
            "job_recommended": [],
            # Set defaults for other fields
            "cv_name": "" if not has_resume else "pending",
            "created_at": created_at,
            "sql": 0,
            "office": 0
        }
        candidates_to_insert.append(candidate_doc)
        
        # If candidate doesn't have a resume, add to list for sending messages
        if not has_resume:
            candidates_needing_resume.append({
                "name": candidate["candidate_name"],
                "phone_number": candidate["phone_number"]
            })
    
    try:
        # Insert the candidates into the database
        collection = mongo.db.candidate
        result = collection.insert_many(candidates_to_insert)
        
        # Send WhatsApp messages to candidates who need to upload resumes
        notification_stats = {
            "total": len(candidates_needing_resume),
            "sent": 0,
            "failed": 0
        }
        
        for candidate in candidates_needing_resume:
            try:
                # Craft a personalized message asking for the resume
                message = f"Hello {candidate['name']},\n\nThank you for your interest in our opportunities at Intelligent Resume Matching! We've created your profile, but we noticed you haven't submitted your resume yet.\n\nPlease upload your resume to complete your profile and enable us to match you with the best job opportunities.\n\nBest regards,\nThe Intelligent Resume Matching Team"
                
                # Send the message
                success = notification_service.send_whatsapp_notification(
                    candidate["phone_number"], 
                    message
                )
                
                if success:
                    notification_stats["sent"] += 1
                else:
                    notification_stats["failed"] += 1
            except Exception as e:
                logger.error(f"Failed to send WhatsApp notification: {str(e)}")
                notification_stats["failed"] += 1
        
        logger.info(f"WhatsApp resume request notifications: {notification_stats}")
        
        return {
            "message": f"Successfully uploaded {len(result.inserted_ids)} candidates",
            "success": True,
            "inserted_count": len(result.inserted_ids),
            "notification_stats": notification_stats
        }
    except Exception as e:
        logger.error(f"Error in bulk uploading candidates: {str(e)}")
        abort(500, message=f"Error uploading candidates: {str(e)}")
