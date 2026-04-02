package feature.register.impl.state

data class RegisterState(
    val isLoading: Boolean = false,
    val isError: Boolean = false,

    val errorMessage: String = "",

    val login: String = "",
    val hasLoginError: Boolean = false,

    val password: String = "",
    val passwordConfirm: String = "",
    val hasPasswordError: Boolean = false,
) {
    val hasErrors: Boolean
        get() = hasLoginError && hasPasswordError
}