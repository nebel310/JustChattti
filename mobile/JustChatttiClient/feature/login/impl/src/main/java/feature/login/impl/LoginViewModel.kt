package feature.login.impl

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import core.common.exceptions.NetworkException
import data.models.UserCreate
import data.models.UserCredentials
import domain.auth.LoginUseCase
import feature.login.impl.state.LoginAction
import feature.login.impl.state.LoginState
import feature.login.impl.state.SideEffect
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class LoginViewModel(
    private val loginUseCase: LoginUseCase
): ViewModel() {
    private val _sideEffect = Channel<SideEffect>()
    val sideEffect = _sideEffect.receiveAsFlow()

    private val _state = MutableStateFlow(LoginState())
    val state = _state.asStateFlow()

    fun processAction(action: LoginAction) {
        viewModelScope.launch {
            when (action) {
                is LoginAction.ChangeLogin -> changeLogin(action.value)
                is LoginAction.ChangePassword -> changePassword(action.value)
                LoginAction.OnLogin -> login()
                LoginAction.OnNoAccount -> {}
                LoginAction.OnForgotPassword -> {}
            }
        }
    }

    private fun changeLogin(value: String) {
        _state.update {
            it.copy(
                login = value,
                hasLoginError = false,
                hasPasswordError = false,
            )
        }
    }

    private fun changePassword(value: String) {
        _state.update {
            it.copy(
                password = value,
                hasLoginError = false,
                hasPasswordError = false,
            )
        }
    }

    private suspend fun login() {
        _state.update { it.copy(isLoading = true) }

        val result = runCatching {
            loginUseCase(
                UserCredentials(
                    login = state.value.login,
                    password = state.value.password
                )
            )
        }

        with(result) {
            onSuccess {
                _sideEffect.send(SideEffect.SuccessLogin)
            }

            onFailure { e ->
                val message = (e as? NetworkException)?.error?.title ?: "Unknown error"
                _state.update { it.copy(errorMessage = message) }
            }
        }

        _state.update { it.copy(isLoading = false) }
    }
}