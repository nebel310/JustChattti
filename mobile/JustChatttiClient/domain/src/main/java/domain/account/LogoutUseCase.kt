package domain.account

import data.local.TokenManager
import data.repositories.user.UsersRepository

class LogoutUseCase(
    private val usersRepository: UsersRepository,
    private val tokenManager: TokenManager
) {
    suspend operator fun invoke() {
        usersRepository.logout()
        tokenManager.clear()
    }
}