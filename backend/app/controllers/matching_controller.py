from app.schemas.matching_schema import (
    ProcessMatchingSchema,
    MatchingSchema,
    MatchingFilterPageSchema,
    MatchingPageSchema,
    MatchingDetailSchema,
    ShortlistNotificationSchema,
)
from app.services import matching_service, notification_service
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import send_file, request
import os

blp = Blueprint("Matching", __name__, description="Matching API")


@blp.route("/process-matching")
class Matching(MethodView):
    @blp.arguments(ProcessMatchingSchema)
    def post(self, matching_data):
        result = matching_service.process_matching(matching_data)
        return result


@blp.route("/data-matching")
class MatchingFilter(MethodView):
    @blp.response(200, MatchingSchema(many=True))
    def get(self):
        result = matching_service.get_all_matching()
        return result

    @blp.arguments(MatchingFilterPageSchema)
    @blp.response(200, MatchingPageSchema)
    def post(self, matching_data):
        result = matching_service.filter_matching_data(matching_data)
        return result


@blp.route("/candidate/<string:candidate_id>/job/<string:job_id>")
class GetMatchingData(MethodView):
    @blp.response(200, MatchingDetailSchema)
    def get(self, candidate_id, job_id):
        result = matching_service.get_matching_data(candidate_id, job_id)
        return result


@blp.route("/matching/export-pdf/<string:job_name>")
class MatchingPDFResource(MethodView):
    def get(self, job_name):
        """Generate and download a PDF report for matching results"""
        try:
            # Get limit parameter from query string, default to 20
            limit = request.args.get('limit', default=20, type=int)
            # Ensure limit is between 1 and 100
            limit = max(1, min(100, limit))
            
            pdf_path = matching_service.generate_matching_pdf(job_name, limit)
            return send_file(
                pdf_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=os.path.basename(pdf_path)
            )
        except Exception as e:
            abort(500, message=str(e))


@blp.route("/matching/shortlist-notify")
class ShortlistNotification(MethodView):
    @blp.arguments(ShortlistNotificationSchema)
    def post(self, notification_data):
        """Send shortlist notifications to top N candidates for a job"""
        try:
            job_name = notification_data["job_name"]
            top_n = notification_data.get("top_n", 5)  # Default to top 5 if not specified
            
            result = notification_service.send_shortlist_notifications(job_name, top_n)
            return result
        except Exception as e:
            abort(500, message=str(e))
