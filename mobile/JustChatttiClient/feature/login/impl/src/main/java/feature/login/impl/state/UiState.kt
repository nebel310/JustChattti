package feature.login.impl.state

data class LoginState(
    val isLoading: Boolean = false,

    val isError: Boolean = false,
    val errorMessage: String = "",

    val login: String = "",
    val hasLoginError: Boolean = false,

    val password: String = "",
    val hasPasswordError: Boolean = false,
)