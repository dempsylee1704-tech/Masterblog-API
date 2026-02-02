from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get("sort")
    direction = request.args.get("direction")

    if sort_field is None and direction is None:
        return jsonify(POSTS), 200

    if sort_field is None or direction is None:
        return jsonify({
            "error": "Both 'sort' and 'direction' must be provided together."
        }), 400

    sort_field = sort_field.strip().lower()
    direction = direction.strip().lower()

    allowed_sort_fields = {"title", "content"}
    allowed_directions = {"asc", "desc"}

    if sort_field not in allowed_sort_fields:
        return jsonify({
            "error": "Invalid sort field. Allowed values are: title, content."
        }), 400

    if direction not in allowed_directions:
        return jsonify({
            "error": "Invalid direction. Allowed values are: asc, desc."
        })
    sorted_posts = POSTS[:]

    reverse = (direction == "desc")

    sorted_posts.sort(key=lambda p: p[sort_field].lower(), reverse=reverse)

    return jsonify(sorted_posts), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid data"}), 400

    missing = []

    title = data.get("title")
    content = data.get("content")
    if title is None or title.strip() == "":
        missing.append("title")

    if content is None or content.strip() == "":
        missing.append("content")

    if missing:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing
        }), 400

    title = title.strip()
    content = content.strip()

    new_id = max(post['id'] for post in POSTS) + 1 if POSTS else 1

    new_post = {
        "id": new_id,
        "title": title,
        "content": content
    }

    POSTS.append(new_post)

    return jsonify(new_post), 201

@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    post_to_delete = None
    for post in POSTS:
        if post["id"] == id:
            post_to_delete = post
            break

    if post_to_delete is None:
        return jsonify({
            "error": f"Post with id {id} not found."
        }), 404

    POSTS.remove(post_to_delete)

    return jsonify({
        "message": f"Post with id {id} has been deleted successfully."
    }), 200

@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    post_to_update = None
    for post in POSTS:
        if post["id"] == id:
            post_to_update = post
            break

    if post_to_update is None:
        return jsonify({
            "error": f"Post with id {id} not found."
        }), 404

    data = request.get_json()
    if data is None:
        return jsonify({
            "error": "Invalid data"
        }), 400

    new_title = data.get("title")
    new_content = data.get("content")

    if new_title is not None and new_title.strip() != "":
        post_to_update["title"] = new_title.strip()

    if new_content is not None and new_content.strip() != "":
        post_to_update["content"] = new_content.strip()

    return jsonify(post_to_update), 200

@app.route('/api/posts/search', methods=['GET'])
def search_for_query():
    title_query = request.args.get("title", "").strip().lower()
    content_query = request.args.get("content", "").strip().lower()

    results = []

    for post in POSTS:
        title_text = post["title"].lower()
        content_text = post["content"].lower()

        matches_title = True
        matches_content = True

        if title_query:
            matches_title = title_query in title_text

        if content_query:
            matches_content = content_query in content_text

        if matches_title and matches_content:
            results.append(post)

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
