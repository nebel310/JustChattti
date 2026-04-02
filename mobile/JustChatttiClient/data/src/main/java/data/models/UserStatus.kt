package data.models

import kotlinx.datetime.LocalDateTime


data class UserStatus(
    val userId: Int,
    val username: String,
    val isOnline: Boolean,
    val lastSeen: LocalDateTime
)
