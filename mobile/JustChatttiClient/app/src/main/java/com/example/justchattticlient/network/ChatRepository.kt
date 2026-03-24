package com.example.justchattticlient.network

import com.example.justchattticlient.data.ChatItemResponse
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import okhttp3.ResponseBody
import retrofit2.Response

import android.util.Log

class ChatRepository(private val chatService: ChatService) {

    private val gson = Gson()

    suspend fun getChats(skip: Int = 0, limit: Int = 50): Result<List<ChatItemResponse>> {
        return try {
            Log.d("ChatRepository", "Загрузка чатов skip=$skip limit=$limit")
            val response: Response<ResponseBody> = chatService.getChats(skip, limit)

            if (response.isSuccessful) {
                val bodyString = response.body()?.string() ?: "[]"
                Log.d("ChatRepository", "JSON: $bodyString")

                val listType = object : TypeToken<List<ChatItemResponse>>() {}.type
                val chats: List<ChatItemResponse> = gson.fromJson(bodyString, listType) ?: emptyList()

                Log.d("ChatRepository", "Получено чатов: ${chats.size}")
                Result.success(chats)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Unknown error"
                Log.e("ChatRepository", "HTTP ${response.code()}: $errorBody")
                Result.failure(Exception("HTTP ${response.code()}: $errorBody"))
            }
        } catch (e: Exception) {
            Log.e("ChatRepository", "Ошибка сети", e)
            Result.failure(e)
        }
    }
}
