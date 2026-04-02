package data.remote.models.user

import com.google.gson.annotations.SerializedName
import kotlinx.datetime.LocalDate
import kotlinx.datetime.LocalDateTime
import kotlinx.serialization.Serializable

@Serializable
internal data class UserResponse(
    val id: Int,
    val username: String,
    @SerializedName("avatar_id")
    val avatarId: Int?,
    val bio: String?,
    val gender: String,
    @SerializedName("birth_date")
    val birthDate: LocalDate?,
    @SerializedName("is_online")
    val isOnline: Boolean,
    @SerializedName("last_seen")
    val lastSeen: LocalDateTime,
    @SerializedName("created_at")
    val createdAt: LocalDateTime,
    @SerializedName("user_metadata")
    val userMetadata: Map<String, String>?
)
