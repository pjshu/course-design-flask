from flask import jsonify


def generate_res(status, data=None):
    return jsonify({
        "status": status,
        "data": data
    })
