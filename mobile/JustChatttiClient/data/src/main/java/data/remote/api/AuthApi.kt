package data.remote.api

import data.remote.models.auth.LoginRequest
import data.remote.models.auth.LoginResponse
import data.remote.models.auth.RefreshTokenRequest
import data.remote.models.auth.RefreshTokenResponse
import data.remote.models.auth.RegisterRequest
import data.remote.models.auth.RegisterResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

internal interface AuthApi {
    @POST("register")
    suspend fun register(@Body user: RegisterRequest): Response<RegisterResponse>

    @POST("login")
    suspend fun login(@Body credentials: LoginRequest): Response<LoginResponse>

    @POST("refresh")
    suspend fun refresh(@Body refreshToken: RefreshTokenRequest): Response<RefreshTokenResponse>
}