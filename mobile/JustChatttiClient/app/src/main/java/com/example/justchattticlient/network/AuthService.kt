package com.example.justchattticlient.network

import com.example.justchattticlient.data.LoginRequest
import okhttp3.ResponseBody
import retrofit2.http.Body
import retrofit2.http.POST
import retrofit2.Response

interface AuthService {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<ResponseBody>
}