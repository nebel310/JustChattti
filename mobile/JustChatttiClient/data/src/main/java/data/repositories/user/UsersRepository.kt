package data.repositories.user

import data.models.User
import data.models.UserStatus
import data.models.UserUpdate

interface UsersRepository {
    suspend fun logout(): Boolean
    suspend fun getCurrentUser(): User
    suspend fun updateUser(updateUser: UserUpdate): User
    suspend fun getUserById(userId: Int): User
    suspend fun getUserStatus(userId: Int): UserStatus
}