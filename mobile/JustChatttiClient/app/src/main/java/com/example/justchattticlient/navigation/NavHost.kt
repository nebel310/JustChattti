package com.example.justchattticlient.navigation

import ChatsViewModel
import androidx.compose.runtime.Composable
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.example.justchattticlient.network.ChatListRepository
import com.example.justchattticlient.network.ChatListService
import com.example.justchattticlient.network.NetworkClient
import com.example.justchattticlient.ui.screens.chatslist.ChatsScreen
import com.example.justchattticlient.ui.screens.login.LoginScreen
import com.example.justchattticlient.ui.screens.registration.RegistrationScreen


@Composable
fun AppNavHost(navController: NavHostController) {
    NavHost(
        navController = navController,
        startDestination = Screen.Login
    ) {
        composable<Screen.Login> {
            LoginScreen(navController = navController)
        }

        composable<Screen.Registration> {
            RegistrationScreen(navController = navController)
        }

        composable<Screen.Chats> {
            val chatListService = NetworkClient.apiRetrofit.create(ChatListService::class.java)
            val repository = ChatListRepository(chatListService)
            val viewModel: ChatsViewModel = androidx.lifecycle.viewmodel.compose.viewModel(
                factory = object : ViewModelProvider.Factory {
                    override fun <T : ViewModel> create(modelClass: Class<T>): T {
                        @Suppress("UNCHECKED_CAST")
                        return ChatsViewModel(repository) as T
                    }
                }
            )

            ChatsScreen(viewModel = viewModel)
        }


    }

}
