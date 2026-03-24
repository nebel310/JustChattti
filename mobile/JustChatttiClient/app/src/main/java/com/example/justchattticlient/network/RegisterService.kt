package com.example.justchattticlient.network

import com.example.justchattticlient.data.RegisterRequest
import com.example.justchattticlient.data.RegisterResult
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface RegisterService {
    @POST("register")
    suspend fun register(@Body request: RegisterRequest): Response<RegisterResult.Success>
}
