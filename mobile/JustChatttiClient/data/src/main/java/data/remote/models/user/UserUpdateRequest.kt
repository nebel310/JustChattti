package data.remote.models.user

import com.google.gson.annotations.SerializedName
import kotlinx.datetime.LocalDate
import kotlinx.serialization.Serializable

@Serializable
internal data class UserUpdateRequest(
    @SerializedName("avatar_id")
    val avatarId: Int?,
    val bio: String?,
    val gender: String?,
    @SerializedName("birth_date")
    val birthDate: LocalDate?,
    @SerializedName("user_metadata")
    val userMetadata: Map<String, String>?
)
