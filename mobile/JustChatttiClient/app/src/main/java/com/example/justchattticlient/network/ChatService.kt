package com.example.justchattticlient.network

import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Query

interface ChatService {
    @GET("chats/")
    suspend fun getChats(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 50
    ): Response<ResponseBody>
}
