package data.models

data class UserCreate(
    val username: String,
    val password: String,
    val passwordConfirm: String,
    val userMetadata: Map<String, String>?
)
