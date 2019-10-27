# app/main/views.py
from app import limiter, db
from flask import jsonify, request, abort
from flask import current_app as app
from app.main import bp
from app.models import Profile
from app.decorators import require_access_level
from app.assertions import assert_valid_schema
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from jsonschema.exceptions import ValidationError as JsonValidationError
import uuid
import time
import datetime

# reject any non-json requests
#@bp.before_request
def only_json():
    if not request.is_json:
        abort(400)

# -----------------------------------------------------------------------------
# helper route - useful for checking status of api in api_server application

@bp.route('/profile/status', methods=['GET'])
@limiter.limit("100/hour")
def system_running():
    app.logger.info("Praise the FSM! The sauce is ready")
    return jsonify({ 'message': 'System running...' }), 200

# -----------------------------------------------------------------------------

@bp.route('/profile', methods=['PUT'])
@limiter.limit("10/hour")
@require_access_level(10, request)
def edit_profile(public_id, request):

    #TODO: data sanitization
    data = request.get_json()

    try:
        profile = Profile.query.filter_by(public_id = public_id).first()
    except (SQLAlchemyError, DBAPIError) as e:
        app.logger.error(e)
        return jsonify({ 'message': 'oopsy, sorry we couldn\'t complete your request' }), 502

    if not profile:
        return jsonify({ 'message': 'Cannot find profile data for this user'}), 404

    ts = time.time()
    datetime_string = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    profile.modified = datetime_string
    if data['about_me']:
        profile.about_me = data['about_me']
    if data['bespoke_avatar']:
        profile.about_me = data['bespoke_avatar']
    if data['standard_avatar']:
        profile.about_me = data['standard_avatar']    

    try:
        #db.session.update(profile)
        db.session.flush()
        db.session.commit()
    except (SQLAlchemyError, DBAPIError) as e:
        app.logger.error(e)
        db.session.rollback()
        return jsonify({ 'message': 'oopsy, something went wrong at our end' }), 422

    return jsonify({ 'message': 'profile details updated successfully' }), 201



# -----------------------------------------------------------------------------
# creates a profile for the authenticated user

@bp.route('/profile', methods=['POST'])
@limiter.limit("10/hour")
@require_access_level(10, request)
def create_profile_for_user(public_id, request):

    #TODO: data sanitization
    data = request.get_json()

#    # check input is valid json
#    try:
#        data = request.get_json()
#    except:
#        return jsonify({ 'message': 'Check ya inputs mate. Yer not valid, Jason'}), 400
#
#    # validate input against json schemas
#    try:
#        assert_valid_schema(data, 'profile')
#
#    except JsonValidationError as err:
#        return jsonify({ 'message': 'Check ya inputs mate.', 'error': err.message }), 400
    ts = time.time()
    datetime_string = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    profile = Profile(public_id = public_id,
                      bespoke_avatar = data.get('bespoke_avatar') or None,
                      standard_avatar = data.get('standard_avatar') or None,
                      about_me = data.get('about_me') or None,
                      created  = datetime_string)

    try:
        db.session.add(profile)
        db.session.flush()
        db.session.commit()
    except (SQLAlchemyError, DBAPIError) as e:
        app.logger.error(e)
        db.session.rollback()
        return jsonify({ 'message': 'oopsy, something went wrong at our end' }), 422
   
    return jsonify({ 'message': 'profile details created successfully' }), 201

# -----------------------------------------------------------------------------

@bp.route('/profile/avatar', methods=['POST', 'PUT'])
@limiter.limit("10/hour")
@require_access_level(10, request)
def upload_avatar_for_user(public_id, request):

    #TODO: data sanitization
    data = request.get_json()    

    if not data:
        return jsonify({ 'message': 'no data supplied' }), 400

    if not data.get('bespoke_avatar') and not data.get('standard_avatar'):
        return jsonify({ 'message': 'please choose at least one type of avatar' }), 400

    try:
        profile = Profile.query.filter_by(public_id = public_id).first()
    except (SQLAlchemyError, DBAPIError) as e:
        app.logger.error(e)
        return jsonify({ 'message': 'oopsy, sorry we couldn\'t complete your request' }), 502

    ts = time.time()
    datetime_string = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    if not profile:
        # new profile
        profile = Profile(about_me = '',
                          created = datetime_string,
                          modified = datetime_string,
                          public_id = public_id)
        if data.get('bespoke_avatar'):
            profile.standard_avatar = None
            profile.bespoke_avatar = data.get('bespoke_avatar')
        elif data.get('standard_avatar'):
            profile.bespoke_avatar = None
            profile.standard_avatar = data.get('standard_avatar')         
        db.session.add(profile)
    else:
        # existing profile
        profile.modified = datetime_string
        if data.get('bespoke_avatar'):
            profile.standard_avatar = None
            profile.bespoke_avatar = data.get('bespoke_avatar')
        elif data.get('standard_avatar'):
            profile.bespoke_avatar = None
            profile.standard_avatar = data.get('standard_avatar')

    try:
        db.session.flush()
        db.session.commit()
    except (SQLAlchemyError, DBAPIError) as e:
        app.logger.error(e)
        db.session.rollback()
        return jsonify({ 'message': 'oopsy, something went wrong at our end' }), 422

    return jsonify({ 'message': 'profile updated' }), 200

# -----------------------------------------------------------------------------

@bp.route('/profile/<uuid:public_id>', methods=['GET'])
@limiter.limit("100/hour")
def get_profile(public_id):

    # convert to string
    public_id = str(public_id)
    profile = None
    try:
        profile = db.session.query(Profile.standard_avatar,
                                   Profile.bespoke_avatar,
                                   Profile.about_me).filter(Profile.public_id == public_id)\
                                                    .first()
    except:
        return jsonify({ 'message': 'oopsy, sorry we couldn\'t complete your request' }), 502

    if not profile:
        message = "no profile found for supplied id ["+profile_id+"]"
        return jsonify({ 'message': message }), 404

    # i prefer to explicitly assign variables returned to ensure no 
    # accidental exposure of private data
    profile_data = {}
    profile_data['standard_avatar'] = profile.standard_avatar
    profile_data['bespoke_avatar'] = profile.bespoke_avatar
    profile_data['about_me'] = profile.about_me

    return jsonify(profile_data), 200

# -----------------------------------------------------------------------------

@bp.route('/profile', methods=['GET'])
@limiter.limit("100/hour")
@require_access_level(10, request)
def get_my_profile(public_id, request):

    # convert to string
    profile = None
    try:
        profile = db.session.query(Profile.standard_avatar,
                                   Profile.bespoke_avatar,
                                   Profile.about_me).filter(Profile.public_id == public_id)\
                                                    .first()
    except Exception as e:
        app.logger.info(e)  
        return jsonify({ 'message': 'oopsy, sorry we couldn\'t complete your request' }), 502

    if not profile:
        message = "no profile found for supplied id"
        return jsonify({ 'message': message }), 404

    # i prefer to explicitly assign variables returned to ensure no 
    # accidental exposure of private data
    profile_data = {}
    profile_data['standard_avatar'] = profile.standard_avatar
    profile_data['bespoke_avatar'] = profile.bespoke_avatar
    profile_data['about_me'] = profile.about_me

    return jsonify(profile_data), 200


# -----------------------------------------------------------------------------
# deletes profile data for the authenticated user

@bp.route('/profile', methods=['DELETE'])
@limiter.limit("10/hour")
@require_access_level(10, request)
def delete_profile_for_user(public_id, request):

    try:
        result = Profile.query.filter(Profile.public_id == public_id)\
                              .delete()
    except SQLAlchemyError as err:
        return jsonify({ 'message': 'naughty, naughty' }), 401

    if result:
        return '', 204

    return jsonify({ 'message': 'nope sorry, that\'s not happening today' }), 401

# -----------------------------------------------------------------------------
# admin routes
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# route for testing rate limit works - generates 429 if more than two calls
# per minute to this route - restricted to admin users and above
@bp.route('/profile/admin/ratelimited', methods=['GET'])
@require_access_level(5, request)
@limiter.limit("0/minute")
def rate_limted(public_id, request):
    return jsonify({ 'message': 'should never see this' }), 200

# -----------------------------------------------------------------------------
# route for anything left over - generates 404

@bp.route('/profile/<everything_left>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def not_found(everything_left):
    message = 'resource ['+everything_left+'] not found'
    return jsonify({ 'message': message }), 404
