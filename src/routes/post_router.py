from flask import request, g, Blueprint, json, Response
from ..shared.Authentication import Auth
from ..models.PostModel import PostModel, PostSchema

post_api = Blueprint('post', __name__)
post_schema = PostSchema()


@post_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
    """
    Create Blogpost Function
    """
    req_data = request.get_json()
    req_data['owner_id'] = g.user.get('id')
    data, error = post_schema.load(req_data)
    if error:
        return custom_response(error, 400)
    post = PostModel(data)
    post.save()
    data = post_schema.dump(post).data
    return custom_response(data, 201)


@post_api.route('/', methods=['GET'])
def get_all():
    """
    Get All Blogposts
    """
    posts = PostModel.get_all_blogposts()
    data = post_schema.dump(posts, many=True).data
    return custom_response(data, 200)


@post_api.route('/<int:blogpost_id>', methods=['GET'])
def get_one(blogpost_id):
    """
    Get A Blogpost
    """
    post = PostModel.get_one_blogpost(blogpost_id)
    if not post:
        return custom_response({'error': 'post not found'}, 404)
    data = post_schema.dump(post).data
    return custom_response(data, 200)


@post_api.route('/<int:blogpost_id>', methods=['PUT'])
@Auth.auth_required
def update(blogpost_id):
    """
    Update A Blogpost
    """
    req_data = request.get_json()
    post = PostModel.get_one_blogpost(blogpost_id)
    if not post:
        return custom_response({'error': 'post not found'}, 404)
    data = post_schema.dump(post).data
    if data.get('owner_id') != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 400)

    data, error = post_schema.load(req_data, partial=True)
    if error:
        return custom_response(error, 400)
    post.update(data)

    data = post_schema.dump(post).data
    return custom_response(data, 200)


@post_api.route('/<int:blogpost_id>', methods=['DELETE'])
@Auth.auth_required
def delete(blogpost_id):
    """
    Delete A Blogpost
    """
    post = PostModel.get_one_blogpost(blogpost_id)
    if not post:
        return custom_response({'error': 'post not found'}, 404)
    data = post_schema.dump(post).data
    if data.get('owner_id') != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 400)

    post.delete()
    return custom_response({'message': 'deleted'}, 204)


def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )
