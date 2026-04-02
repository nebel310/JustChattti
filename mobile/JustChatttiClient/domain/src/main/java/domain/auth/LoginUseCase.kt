package domain.auth

import data.local.TokenManager
import data.models.UserCredentials
import data.repositories.auth.AuthUserRepository

class LoginUseCase(
    private val authRepository: AuthUserRepository,
    private val tokenManager: TokenManager
) {
    suspend operator fun invoke(credentials: UserCredentials) {
        authRepository.logInUser(credentials).let { tokenData ->
            tokenData.accessToken?.let { tokenManager.setAccessToken(it) }
            tokenData.refreshToken?.let { tokenManager.setAccessToken(it) }
        }
    }
}