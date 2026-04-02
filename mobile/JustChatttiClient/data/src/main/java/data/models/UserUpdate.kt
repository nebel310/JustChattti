package data.models

import kotlinx.datetime.LocalDate

data class UserUpdate(
    val avatarId: Int?,
    val bio: String?,
    val gender: String?,
    val birthDate: LocalDate?,
    val userMetadata: Map<String, String>?
)
