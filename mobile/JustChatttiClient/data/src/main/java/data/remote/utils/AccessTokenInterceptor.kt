package data.remote.utils

import data.local.TokenManager
import okhttp3.Interceptor
import okhttp3.Response

class AccessTokenInterceptor(
    private val tokenManager: TokenManager
): Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request().newBuilder()

        val token = tokenManager.getAccessTokenBlocking() ?: ""
        request.addHeader("Authorization", "Bearer $token")

        return chain.proceed(request.build())
    }
}