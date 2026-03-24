package com.example.justchattticlient.navigation


import kotlinx.serialization.Serializable

@Serializable
sealed interface Screen {
    @Serializable data object Login : Screen
    @Serializable data object Registration : Screen

    @Serializable data object Chats : Screen
}
