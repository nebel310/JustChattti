package com.example.justchattticlient.network

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.POST

data class FCMRegisterRequest(val fcm_token: String, val device_id: String?)
data class FCMUnregisterRequest(val fcm_token: String)
data class FCMRegisterResponse(val success: Boolean, val message: String)

interface FCMService {
    @POST("/fcm/register")
    suspend fun registerToken(@Body request: FCMRegisterRequest): Response<FCMRegisterResponse>

    @DELETE("/fcm/unregister")
    suspend fun unregisterToken(@Body request: FCMUnregisterRequest): Response<Unit>
}