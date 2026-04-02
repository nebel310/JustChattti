package feature.login.impl.state

sealed interface SideEffect {
    data object SuccessLogin: SideEffect
    data object NavigateToRegister: SideEffect
    data object NavigateToForgotPassword: SideEffect
}