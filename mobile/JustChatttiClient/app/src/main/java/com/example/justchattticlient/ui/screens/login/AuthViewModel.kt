package com.example.justchattticlient.ui.screens.login

import android.app.Application
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.justchattticlient.data.LoginRequest
import com.example.justchattticlient.data.LoginResult
import com.example.justchattticlient.data.TokenManager
import com.example.justchattticlient.network.AuthRepository
import kotlinx.coroutines.launch

class AuthViewModel(application: Application) : AndroidViewModel(application) {

    private val tokenManager = TokenManager(getApplication())

    private val repository = AuthRepository(tokenManager)

    var loginResult by mutableStateOf<LoginResult?>(null)
        private set

    fun doLogin(login: String, password: String) {
        viewModelScope.launch {
            val logindata = LoginRequest(
                password = password,
                username = login
            )
            // Репозиторий внутри себя сам сохранит токены в tokenManager
            val result = repository.login(logindata)
            loginResult = result
        }
    }
}
