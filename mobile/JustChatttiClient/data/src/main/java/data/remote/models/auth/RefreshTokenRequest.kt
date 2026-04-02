package data.remote.models.auth

import com.google.gson.annotations.SerializedName
import kotlinx.serialization.Serializable

@Serializable
internal data class RefreshTokenRequest(
    @SerializedName("refresh_token")
    val refreshToken: String
)
