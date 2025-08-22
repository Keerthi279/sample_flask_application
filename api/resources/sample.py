from flask import request, jsonify, Blueprint
import services.sample as sample_service
# Create a Blueprint
sample_bp = Blueprint('sample_bp', __name__)


# Get all users
@sample_bp.route('/', methods=['GET'])
def get_samples():
    sample_service.get_records(dataset_id, as_of_date)
    return jsonify(result)

