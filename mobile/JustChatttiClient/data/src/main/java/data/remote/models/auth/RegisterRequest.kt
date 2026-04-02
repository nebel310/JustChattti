package data.remote.models.auth

import com.google.gson.annotations.SerializedName
import kotlinx.serialization.Serializable

@Serializable
internal data class RegisterRequest(
    val username: String,
    val password: String,
    @SerializedName("password_confirm")
    val passwordConfirm: String,
    @SerializedName("user_metadata")
    val userMetadata: Map<String, String>?
)
