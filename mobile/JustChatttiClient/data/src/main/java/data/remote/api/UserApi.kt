package data.remote.api

import data.remote.models.auth.LogoutResponse
import data.remote.models.user.PublicUserResponse
import data.remote.models.user.UserResponse
import data.remote.models.user.UserStatusResponse
import data.remote.models.user.UserUpdateRequest
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.Path

internal interface UserApi {
    @POST("logout")
    suspend fun logout(): Response<LogoutResponse>

    @GET("me")
    suspend fun getMe(): Response<UserResponse>

    @PATCH("user-update")
    suspend fun updateUser(
        @Body body: UserUpdateRequest
    ): Response<UserResponse>

    @GET("users/{user_id}")
    suspend fun getUserById(
        @Path("user_id") userId: Int
    ): Response<PublicUserResponse>

    @GET("users/{user_id}/status")
    suspend fun getUserStatus(
        @Path("user_id") userId: Int
    ): Response<UserStatusResponse>
}