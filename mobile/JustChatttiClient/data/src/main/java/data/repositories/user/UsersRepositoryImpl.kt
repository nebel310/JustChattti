package data.repositories.user

import data.local.TokenManager
import data.models.User
import data.models.UserStatus
import data.models.UserUpdate
import data.models.toExternal
import data.remote.api.UserApi
import data.remote.models.user.UserUpdateRequest
import data.remote.utils.handle

internal class UsersRepositoryImpl(
    private val userApi: UserApi,
    private val tokenManager: TokenManager
): UsersRepository {
    override suspend fun logout(): Boolean {
        return userApi.logout()
            .handle {
                transformSuccess { it.success }
            }
    }

    override suspend fun getCurrentUser(): User {
        return userApi.getMe()
            .handle {
                transformSuccess { it.toExternal() }
            }
    }

    override suspend fun updateUser(updateUser: UserUpdate): User {
        return userApi.updateUser(
            UserUpdateRequest(
                avatarId = updateUser.avatarId,
                bio = updateUser.bio,
                gender = updateUser.gender,
                birthDate = updateUser.birthDate,
                userMetadata = updateUser.userMetadata
            )
        )
            .handle {
                transformSuccess { it.toExternal() }
            }
    }

    override suspend fun getUserById(userId: Int): User {
        return userApi.getUserById(userId)
            .handle {
                transformSuccess {
                    User(
                        id = it.id,
                        username = it.username,
                        avatarId = it.avatarId,
                        bio = it.bio,
                        gender = it.gender,
                        birthDate = it.birthDate,
                        isOnline = it.isOnline,
                        lastSeen = it.lastSeen,
                        createdAt = it.createdAt,
                        userMetadata = it.userMetadata
                    )
                }
            }
    }

    override suspend fun getUserStatus(userId: Int): UserStatus {
        return userApi.getUserStatus(userId)
            .handle {
                transformSuccess {
                    UserStatus(
                        userId = it.userId,
                        username = it.username,
                        isOnline = it.isOnline,
                        lastSeen = it.lastSeen
                    )
                }
            }
    }
}