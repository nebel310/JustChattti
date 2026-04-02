package data.remote.utils

import data.local.TokenManager
import data.repositories.auth.AuthUserRepository
import kotlinx.coroutines.runBlocking
import okhttp3.Authenticator
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route

class TokenAuthenticator(
    private val tokenManager: TokenManager,
    private val authRepository: AuthUserRepository
) : Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        val refreshToken = runBlocking { tokenManager.getRefreshToken() } ?: return null

        val newTokensData = runBlocking {
            try {
                authRepository.refreshAccessToken(refreshToken = refreshToken)
            } catch (e: Exception) {
                null
            }
        } ?: return null

        newTokensData.accessToken?.let {
            runBlocking {
                tokenManager.setAccessToken(newTokensData.accessToken)
            }
        }

        return response.request.newBuilder()
            .header("Authorization", "Bearer ${newTokensData.accessToken}")
            .build()
    }
}