package com.example.justchattticlient.data


data class ChatItemResponse(
    val id: Int,
    val name: String,
    val chat_type: String,
    val avatar_id: Int?,
    val avatar_url: String?,
    val created_by_id: Int,
    val created_at: String,
    val updated_at: String,
    val unread_count: Int,
    val last_message: LastMessage?
)

data class LastMessage(
    val content: String,
    val created_at: String,
    val id: Int,
    val message_type: String,
    val sender_id: Int
)

sealed class ChatsResult {
    object Loading : ChatsResult()
    data class Success(val chats: List<ChatItemResponse>) : ChatsResult()
    data class Error(val message: String) : ChatsResult()
}
