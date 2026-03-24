package com.example.justchattticlient.network

import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface ChatListService {
    @GET("chats/{chat_id}/messages")
    suspend fun getMessages(
        @Path("chat_id") chatId: Int,
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 50,
        @Query("before") before: String? = null
    ): Response<ResponseBody>
}