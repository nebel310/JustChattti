package data.remote.models.auth

import com.google.gson.annotations.SerializedName
import kotlinx.serialization.Serializable

@Serializable
internal data class RegisterResponse(
    val success: Boolean,
    val message: String,
    @SerializedName("user_id")
    val userId: Int
)
