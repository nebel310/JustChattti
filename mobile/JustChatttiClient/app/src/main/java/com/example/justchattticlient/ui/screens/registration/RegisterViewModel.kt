package com.example.justchattticlient.ui.screens.registration

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.justchattticlient.data.RegisterRequest
import com.example.justchattticlient.data.RegisterResult
import com.example.justchattticlient.data.SomeUserData
import com.example.justchattticlient.network.RegisterRepository
import kotlinx.coroutines.launch
import kotlin.String

class RegisterViewModel: ViewModel() {
    private val repository = RegisterRepository()
    var registerResult by mutableStateOf<RegisterResult?>(null)
        private set
    fun doRegister(password: String,
                   password_confirm: String,
                   user_metadata: SomeUserData,
                   username: String)
    {
        viewModelScope.launch {
            val registerdata = RegisterRequest(
                password = password,
                password_confirm = password_confirm,
                user_metadata = user_metadata,
                username = username
            )
            val result = repository.register(registerdata)
            registerResult = result
        }
    }
}