package data.remote.models.auth

import kotlinx.serialization.Serializable

@Serializable
internal data class LogoutResponse(
    val success: Boolean
)
