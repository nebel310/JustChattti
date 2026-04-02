package feature.login.impl.state

sealed interface LoginAction {
    data class ChangeLogin(val value: String): LoginAction
    data class ChangePassword(val value: String): LoginAction
    data object OnLogin: LoginAction
    data object OnNoAccount: LoginAction
    data object OnForgotPassword: LoginAction
}