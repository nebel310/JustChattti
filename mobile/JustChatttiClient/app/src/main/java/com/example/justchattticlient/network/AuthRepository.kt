package com.example.justchattticlient.network

import com.example.justchattticlient.data.LoginRequest
import com.example.justchattticlient.data.LoginResult
import com.example.justchattticlient.data.TokenManager
import com.google.gson.Gson

class AuthRepository(private val tokenManager: TokenManager) {
    private val authService = NetworkClient.authRetrofit.create(AuthService::class.java)
    private val gson = Gson()

    suspend fun login(request: LoginRequest): LoginResult {
        return try {
            val response = authService.login(request)
            val responseBody = response.body()?.string()
            val errorBody = response.errorBody()?.string()

            when (response.code()) {
                200 -> {
                    val res = gson.fromJson(responseBody, LoginResult.Success::class.java)
                    tokenManager.saveTokens(
                        res.access_token, res.refresh_token)
                    res
                }
                400 -> gson.fromJson(errorBody, LoginResult.Error400::class.java)
                422 -> gson.fromJson(errorBody, LoginResult.Error422::class.java)
                else -> LoginResult.Error500("Ошибка: ${response.code()}")
            }
        } catch (e: Exception) {
            LoginResult.Error500("Нет связи: ${e.message}")
        }
    }
}

