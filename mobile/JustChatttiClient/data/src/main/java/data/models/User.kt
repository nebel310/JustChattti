package data.models

import data.remote.models.user.UserResponse
import kotlinx.datetime.LocalDate
import kotlinx.datetime.LocalDateTime
import kotlin.Int

data class User(
    val id: Int,
    val username: String,
    val avatarId: Int?,
    val bio: String?,
    val gender: String?,
    val birthDate: LocalDate?,
    val isOnline: Boolean,
    val lastSeen: LocalDateTime,
    val createdAt: LocalDateTime,
    val userMetadata: Map<String, String>?
)

internal fun UserResponse.toExternal() = User(
    id = id,
    username = username,
    avatarId = avatarId,
    bio = bio,
    gender = gender,
    birthDate = birthDate,
    isOnline = isOnline,
    lastSeen = lastSeen,
    createdAt = createdAt,
    userMetadata = userMetadata
)
