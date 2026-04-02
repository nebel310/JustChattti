package feature.register.impl

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import core.common.exceptions.NetworkException
import core.common.exceptions.isBadRequest
import data.models.UserCreate
import domain.auth.RegisterUseCase
import feature.register.impl.state.RegisterAction
import feature.register.impl.state.RegisterState
import feature.register.impl.state.SideEffect
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class RegisterViewModel(
    private val registerUseCase: RegisterUseCase
): ViewModel() {
    private val _sideEffect = Channel<SideEffect>()
    val sideEffect = _sideEffect.receiveAsFlow()

    private val _state = MutableStateFlow(RegisterState())
    val state = _state.asStateFlow()

    fun processAction(action: RegisterAction) {
        viewModelScope.launch {
            when (action) {
                RegisterAction.OnRegister -> register()
                is RegisterAction.ChangeLogin -> changeLogin(action.value)
                is RegisterAction.ChangePassword -> changePassword(action.value)
                is RegisterAction.ChangePasswordConfirm -> changePasswordConfirm(action.value)
                RegisterAction.HasAccount -> {
                    _sideEffect.send(SideEffect.HasAccount)
                }
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

    private fun changePasswordConfirm(value: String) {
        _state.update {
            it.copy(
                passwordConfirm = value,
                hasLoginError = false,
                hasPasswordError = false,
            )
        }
    }

    private fun register() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }

            val result = runCatching {
                registerUseCase(
                    UserCreate(
                        password = state.value.password,
                        passwordConfirm = state.value.passwordConfirm,
                        username = state.value.login,
                        userMetadata = null
                    )
                )
            }

            result.onSuccess {
                _sideEffect.send(SideEffect.SuccessRegister)
            }

            result.onFailure { e ->
                val message = (e as? NetworkException)?.error?.title ?: "Unknown error"
                _state.update { it.copy(errorMessage = message) }
            }

            _state.update { it.copy(isLoading = false) }
        }
    }
}