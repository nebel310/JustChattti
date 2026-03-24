package com.example.justchattticlient.data

data class MessagesResponse(
    val messages: List<Message>,
    val total: Int,
    val page: Int,
    val page_size: Int,
    val has_more: Boolean
)


data class Message(
    val id: Int,
    val chat_id: Int,
    val content: String,
    val sender_id: Int,
    val sender_username: String,
    val message_type: String,
    val status: String,
    val created_at: String,
    val updated_at: String,
    val edited: Boolean
)
