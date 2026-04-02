package core.common.exceptions


fun Throwable.isBadRequest(): Boolean {
    return this is NetworkException && this.error.status == 400
}

fun Throwable.isUnauthorized(): Boolean {
    return this is NetworkException && this.error.status == 401
}

fun Throwable.isNotFound(): Boolean {
    return this is NetworkException && this.error.status == 404
}

fun Throwable.isNotFoundOrEmpty(): Boolean {
    return this is NetworkException && this.error.status == 404
}

fun Throwable.isServerError(): Boolean {
    return this is NetworkException && this.error.status >= 500
}