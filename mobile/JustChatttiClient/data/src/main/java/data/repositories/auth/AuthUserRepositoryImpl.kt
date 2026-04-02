package data.repositories.auth

import data.local.TokenManager
import data.models.TokenData
import data.models.UserCreate
import data.models.UserCredentials
import data.remote.api.AuthApi
import data.remote.models.auth.LoginRequest
import data.remote.models.auth.RefreshTokenRequest
import data.remote.models.auth.RegisterRequest
import data.remote.utils.handle
import kotlin.String

internal class AuthUserRepositoryImpl(
    private val authApi: AuthApi,
    private val tokenManager: TokenManager
) : AuthUserRepository {
    override suspend fun refreshAccessToken(refreshToken: String): TokenData {
        return authApi.refresh(
            RefreshTokenRequest(refreshToken)
        ).handle {
            transformSuccess {
                TokenData(accessToken = it.accessToken)
            }
        }
    }

    override suspend fun registerUser(user: UserCreate): TokenData {
        println("-----------------")
        println(user.password)
        println(user.passwordConfirm)
        return authApi.register(
            RegisterRequest(
                password = user.password,
                passwordConfirm = user.passwordConfirm,
                userMetadata = user.userMetadata,
                username = user.username
            )
        ).handle {
            transformSuccess {
                TokenData(userId = it.userId)
            }
        }
    }

    override suspend fun logInUser(credentials: UserCredentials): TokenData {
        return authApi.login(
            LoginRequest(
                username = credentials.login,
                password = credentials.password
            )
        ).handle {
            transformSuccess {
                TokenData(
                    accessToken = it.accessToken,
                    refreshToken = it.refreshToken
                )
            }
        }
    }
}