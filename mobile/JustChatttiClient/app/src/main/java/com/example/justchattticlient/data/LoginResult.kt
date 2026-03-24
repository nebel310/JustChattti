package com.example.justchattticlient.data

sealed class LoginResult {
    data class Success(
        val success: Boolean,
        val message: String,
        val access_token: String,
        val refresh_token: String,
        val token_type: String
    ) : LoginResult()

    data class Error400 (
        val detail: String
    ) : LoginResult()

    data class Error422(
        val detail: List<ErrorValidation>
    ) : LoginResult()

    data class Error500(
        val detail: String
    ) : LoginResult()
}



