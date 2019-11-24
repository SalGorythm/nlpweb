from flask import jsonify


def validation_errors(errors):
    return json_error(code=400, status="error", message="Validations error(s) occurred.", errors=errors)


def json_error(results={}, code=404, status="error", message="", errors=[], hand_shake=0):
    return jsonify({"results": results, "code": code, "status": status, "message": message, "errors": errors,
                    "hand_shake": hand_shake})


def json_success(results={}, code=200, status="success", message="", errors=[], is_json=0):
    if is_json:
        return json_error(code=400, status="error", message="Validations error(s) occurred.", errors=errors)
    return jsonify({"results": results, "code": code, "status": status, "message": message, "errors": errors})
