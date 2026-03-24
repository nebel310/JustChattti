package com.example.justchattticlient.data

sealed class RegisterResult {
    data class Success(
        val success: Boolean,
        val user_id: Int,
        val message: String,
    ) : RegisterResult()

    data class Error400 (
        val detail: String
    ) : RegisterResult()

    data class Error422(
        val detail: List<ErrorValidation>
    ) : RegisterResult()

    data class Error500(
        val detail: String
    ) : RegisterResult()
}

