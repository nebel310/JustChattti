package com.example.justchattticlient.network

import com.example.justchattticlient.data.LoginResult
import com.example.justchattticlient.data.RegisterRequest
import com.example.justchattticlient.data.RegisterResult
import com.google.gson.Gson

class RegisterRepository {
    private val registerService = NetworkClient.authRetrofit.create(RegisterService::class.java)

    suspend fun register(request: RegisterRequest): RegisterResult {
        return try {
            val response = registerService.register(request)

            if (response.isSuccessful) {
                response.body() ?: RegisterResult.Error500("Пустой ответ от сервера")
            } else {
                val errorBody = response.errorBody()?.string()
                val code = response.code()

                when (code) {
                    400 -> Gson().fromJson(errorBody, RegisterResult.Error400::class.java)
                    422 -> Gson().fromJson(errorBody, RegisterResult.Error422::class.java)
                    else -> RegisterResult.Error500("Ошибка $code: ${response.message()}")
                }
            }
        } catch (e: Exception) {
            RegisterResult.Error500("Нет связи с сервером: ${e.message}")
        }
    }
}


