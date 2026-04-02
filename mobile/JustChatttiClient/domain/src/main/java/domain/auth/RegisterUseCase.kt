package domain.auth

import data.local.TokenManager
import data.models.UserCreate
import data.repositories.auth.AuthUserRepository

class RegisterUseCase(
    private val authRepository: AuthUserRepository,
    private val tokenManager: TokenManager
) {
    suspend operator fun invoke(user: UserCreate) {
        authRepository.registerUser(user).let { tokenData ->
            tokenData.userId?.let { tokenManager.setUserId(it) }
        }
    }
}