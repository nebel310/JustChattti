package data.remote.models.user

import com.google.gson.annotations.SerializedName
import kotlinx.datetime.LocalDateTime
import kotlinx.serialization.Serializable

@Serializable
internal data class UserStatusResponse(
    @SerializedName("user_id")
    val userId: Int,
    val username: String,
    @SerializedName("is_online")
    val isOnline: Boolean,
    @SerializedName("last_seen")
    val lastSeen: LocalDateTime
)
